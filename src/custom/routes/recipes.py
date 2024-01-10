from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.core.start import db
from src.core.auth import validate_session
from src.core.methods import api_output, check_stale_data, append_user_credentials
from src.core.models import  Recipes, RecipeIngredients
from src.core.schemas import APIOutput, DBOutput, DeleteFilters, SuccessMessages, WhereConditions
from src.custom.queries import RECIPE_COMPOSITION_LOADED_QUERY as LOADED_QUERY\
                            , RECIPE_COMPOSITION_SNAPSHOT_QUERY as SNAPSHOT_QUERY\
                            , RECIPE_COMPOSITION_EMPTY_QUERY as EMPTY_QUERY
from src.custom.schemas import CSTUpsertRecipe, CSTDeleteRecipeInput

import pandas as pd
import os


customRecipes_router = APIRouter()


SELF_PATH = os.path.dirname(os.path.abspath(__file__))

@customRecipes_router.post("/custom/recipes/upsert_recipe")
async def submit_recipe(input: CSTUpsertRecipe, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Update a recipe in the database.
    """
    form_data = {key: value for key, value in input.form_data.items() if value != ''}
    append_user_credentials(form_data, id_user)

    timestamp = input.reference_time

    keep_columns = [key for key in RecipeIngredients.__annotations__.keys()]

    curr_recipe_ingredients = pd.DataFrame(input.recipe_ingredients_rows)
    curr_recipe_ingredients = curr_recipe_ingredients.drop(['id'], axis=1)
    curr_recipe_ingredients = curr_recipe_ingredients.rename(columns={'id_recipe_ingredient': 'id'})
    curr_recipe_ingredients = curr_recipe_ingredients[keep_columns]

    @api_output
    @db.catching(messages=SuccessMessages('Recipe updated successfully.'))
    def _submit_recipe(form_data, timestamp: str, curr_recipe_ingredients: pd.DataFrame) -> DBOutput:

        # check for stale form data
        if form_data.get('id'):
            recipe_filters = WhereConditions(and_={'id': [form_data.get('id')]})
            check_stale_data(Recipes, recipe_filters, timestamp)


        # upsert recipe
        recipe_object = db.upsert(Recipes, [form_data.copy()], single=True)


        # check for stale recipe ingredients
        if form_data.get('id'):
            stale_recipe_ingredients_filters = WhereConditions(and_={'id_recipe': [form_data.get('id')]})
            old_recipe_ingredients = check_stale_data(RecipeIngredients, stale_recipe_ingredients_filters, timestamp)
        else:
            old_recipe_ingredients = pd.DataFrame(columns=curr_recipe_ingredients.columns)


        # build insert, update, and delete dataframes
        merged_df = old_recipe_ingredients.merge(curr_recipe_ingredients, how='outer', indicator=True)
        merged_df['id_recipe'] = recipe_object.id
        merged_df['id'] = merged_df['id'].astype('Int64')    

        insert_df = merged_df.query('_merge == "right_only"')\
                             .drop(['id', 'created_at', 'updated_at', '_merge'], axis=1, errors='ignore')
        update_df = merged_df.query('_merge == "both"')\
                            .drop(['updated_at', '_merge'], axis=1, errors='ignore')
        delete_df = merged_df.query('_merge == "left_only"')\
                            .drop('_merge', axis=1, errors='ignore')
        

        # append user credentials
        append_user_credentials(insert_df, id_user)
        append_user_credentials(update_df, id_user)


        # filter out data from other users
        if 'created_by' in insert_df.columns:   
            insert_df = insert_df[insert_df['created_by'] == id_user]

        if 'created_by' in update_df.columns:
            update_df = update_df[update_df['created_by'] == id_user]

        if 'created_by' in delete_df.columns:
            delete_df = delete_df[delete_df['created_by'] == id_user]


        # perform operations
        if not insert_df.empty: db.insert(RecipeIngredients, insert_df.to_dict('records'))
        if not update_df.empty: db.update(RecipeIngredients, update_df.to_dict('records'))
        if not delete_df.empty: db.delete(RecipeIngredients, DeleteFilters(field='id', values=delete_df['id'].tolist()))

        db.session.commit()

        return {
            'form_data': recipe_object,
            'recipes_data': db.query(Recipes),
            'recipe_ingredients_loaded': db.query(None, LOADED_QUERY(recipe_object.id, id_user)),
            'recipe_ingredients_snapshot': db.query(None, SNAPSHOT_QUERY(recipe_object.id, id_user)),
        }
    
    return _submit_recipe(form_data, timestamp, curr_recipe_ingredients)


@customRecipes_router.delete("/custom/recipes/delete_recipe")
async def delete_recipe(input: CSTDeleteRecipeInput, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Delete a recipe from the database.
    """

    @api_output
    @db.catching(messages=SuccessMessages('Recipe deleted successfully.'))
    def delete_recipe_touch(recipe_filters: DeleteFilters, composition_filters: DeleteFilters) -> DBOutput:
        composition_where = WhereConditions(and_={composition_filters.field: composition_filters.values, 'created_by': [id_user]})
        recipe_where = WhereConditions(and_={recipe_filters.field: recipe_filters.values, 'created_by': [id_user]})

        db.delete(RecipeIngredients, composition_where)
        db.delete(Recipes, recipe_where)
        db.session.commit()

        return {
            'recipes_data': db.query(Recipes),
            'recipe_ingredients_data': db.query(None, EMPTY_QUERY(id_user)),
        }

    return delete_recipe_touch(input.recipe, input.composition)