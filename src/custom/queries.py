# This area is meant for complex queries that are not covered by simple usage of models as
# statements. Therefore, expressions are used to create the queries. The queries are then
# imported into the CRUD router for use.

from sqlmodel import select, func, literal, case
from src.core.models import Units, Ingredients, RecipeIngredients


# These queries allow for a single table to exhibit all ingredients, including those that are not part of the recipe
# while also allowing for the recipe ingredients to be quantified. The division between three states is necessary
# to allow for state comparisons. One for when no Recipe is selected, another for when a recipe has been clicked,
# and the last to compare updates to the recipe ingredients.

RECIPE_COMPOSITION_EMPTY_QUERY = lambda id_user: select(
    Ingredients.id.label('id'),
    literal(None).label('id_recipe_ingredient'),
    literal(None).label('id_recipe'),
    Ingredients.id.label('id_ingredient'),
    Ingredients.name.label('name'),
    Ingredients.description.label('description'),
    Ingredients.type.label('type'),
    literal(0).label('quantity'),
    literal(None).label('id_unit')
).select_from(
    Ingredients
).outerjoin(
    RecipeIngredients, RecipeIngredients.id_ingredient == Ingredients.id
).where(
    Ingredients.created_by == id_user
).group_by(
    Ingredients.id
).order_by(Ingredients.name)


RECIPE_COMPOSITION_LOADED_QUERY = lambda id_recipe, id_user: select(
    Ingredients.id.label('id'),
    func.MAX(case((RecipeIngredients.id_recipe == id_recipe, RecipeIngredients.id), else_=None)).label('id_recipe_ingredient'),
    literal(id_recipe).label('id_recipe'),
    Ingredients.id.label('id_ingredient'),
    Ingredients.name.label('name'),
    Ingredients.description.label('description'),
    Ingredients.type.label('type'),
    func.COALESCE(func.MAX(case((RecipeIngredients.id_recipe == id_recipe, RecipeIngredients.quantity), else_=None)), 0).label('quantity'),
    func.MAX(case((RecipeIngredients.id_recipe == id_recipe, RecipeIngredients.id_unit), else_=None)).label('id_unit')
).select_from(
    Ingredients
).outerjoin(
        RecipeIngredients, RecipeIngredients.id_ingredient == Ingredients.id
).outerjoin(
        Units, Units.id == RecipeIngredients.id_unit
).where(
    Ingredients.created_by == id_user
).group_by(
        Ingredients.id
).order_by(Ingredients.name)


RECIPE_COMPOSITION_SNAPSHOT_QUERY = lambda id_recipe, id_user: select(
    Ingredients.id.label('id'),
    RecipeIngredients.id.label('id_recipe_ingredient'),
    RecipeIngredients.id_recipe.label('id_recipe'),
    Ingredients.id.label('id_ingredient'),
    Ingredients.name.label('name'),
    Ingredients.description.label('description'),
    Ingredients.type.label('type'),
    case(
        (RecipeIngredients.id_recipe == id_recipe, RecipeIngredients.quantity),
        else_=0
    ).label('quantity'),
    case(
        (RecipeIngredients.id_recipe == id_recipe, Units.id),
        else_=None
    ).label('id_unit')
).select_from(
    Ingredients
).outerjoin(
    RecipeIngredients, RecipeIngredients.id_ingredient == Ingredients.id
).outerjoin(
    Units, Units.id == RecipeIngredients.id_unit
).where(
    RecipeIngredients.id_recipe == id_recipe
    , RecipeIngredients.quantity > 0
    , Ingredients.created_by == id_user
).order_by(Ingredients.name)