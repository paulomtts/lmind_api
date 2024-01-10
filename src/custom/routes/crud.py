from fastapi import APIRouter, Depends

from src.core.models import Categories, Units, Recipes, Ingredients, RecipeIngredients
from src.core.schemas import DBOutput, APIOutput, CRUDSelectInput, CRUDDeleteInput, CRUDInsertInput, CRUDUpdateInput, SuccessMessages
from src.core.methods import api_output, append_user_credentials
from src.core.auth import validate_session
from src.core.start import db
from src.custom.queries import RECIPE_COMPOSITION_EMPTY_QUERY, RECIPE_COMPOSITION_LOADED_QUERY, RECIPE_COMPOSITION_SNAPSHOT_QUERY

from collections import namedtuple


customCrud_router = APIRouter()


TABLE_MAP = {
    'categories': Categories
    , 'units': Units
    , 'recipes': Recipes
    , 'ingredients': Ingredients
    , 'recipe_ingredients': RecipeIngredients
}

ComplexQuery = namedtuple('ComplexQuery', ['statement', 'name'])
QUERY_MAP = {
    'recipe_composition_empty': ComplexQuery(RECIPE_COMPOSITION_EMPTY_QUERY, 'empty Recipe composition')
    , 'recipe_composition_loaded': ComplexQuery(RECIPE_COMPOSITION_LOADED_QUERY, 'loaded Recipe composition')
    , 'recipe_composition_snapshot': ComplexQuery(RECIPE_COMPOSITION_SNAPSHOT_QUERY, 'Recipe')
}


@customCrud_router.post("/custom/crud/insert")
async def crud_insert(input: CRUDInsertInput, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Inserts data into the specified table.

    <h3>Args:</h3>
        <ul>
        <li>table_name (str): The name of the table to insert data into.</li>
        <li>body (dict): Data in the form of a list of dictionaries.</li>
        </ul>

    <h3>Returns:</h3>
        <ul>
        <li>JSONResponse: The JSON response containing the inserted data and a message.</li>
        </ul>
    """
    table_cls = TABLE_MAP.get(input.table_name)
    
    messages = SuccessMessages(
        client=f"Successfuly submited to {input.table_name.capitalize()}."
        , logger=f"Insert in <{input.table_name.capitalize()}> was successful. Data: {input.data}"
    )

    append_user_credentials(input.data, id_user)
    
    @api_output
    @db.catching(messages=messages)
    def crud__insert(table_cls, data) -> DBOutput:
        return db.insert(table_cls, data)
    
    return crud__insert(table_cls, input.data)


@customCrud_router.post("/custom/crud/select")
async def crud_select(input: CRUDSelectInput, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Selects data from a specified table in the database based on the provided filters.

    The parameters should be formatted as follows:
    <pre>
    <code>
    {
        "lambda_args": {
            "arg1": "value1",
            "arg2": "value2",
        }
        "filters": {
            "or": {
                "name": ["value1", "value2"],
            },
            "and": {
                "id": [1]
            },
            "like": {
                "name": ["aaa", "bbb"],
            },
            "not_like": {
                "name": ["ccc"],
            },      
        }
    }
    </code>
    </pre>

    In case of no filters, simply omit the "filters" key.

    <h3>Args:</h3>
        <ul>
        <li>response (Response): The response object.</li>
        <li>table_name (str): The name of the table to select data from.</li>
        <li>data (dict): The request body containing the filters and other parameters.</li>
        </ul>
        
    <h3>Returns:</h3>
        <ul>
        <li>JSONResponse: The response containing the selected data and a message.</li>
        </ul>
    """

    input.lambda_kwargs['id_user'] = id_user

    table_cls = TABLE_MAP.get(input.table_name)

    query = QUERY_MAP.get(input.table_name, ComplexQuery(None, None))
    statement = query.statement if not callable(query.statement)\
                                else query.statement(**input.lambda_kwargs if input.lambda_kwargs else {}) 
    messages = SuccessMessages(
        client=f"{input.table_name.capitalize()[:-1]} retrieved." if table_cls else f"{query.name.capitalize()} retrieved."
        , logger=f"Querying <{input.table_name}> was succesful! Filters: {input.filters}"
    )

    if isinstance(input.filters.and_, dict):
        input.filters.or_['created_by'] = [id_user, 'system']

    @api_output
    @db.catching(messages=messages)
    def crud__select(table_cls, statement, filters):
        return db.query(table_cls=table_cls, statement=statement, filters=filters)

    return crud__select(table_cls, statement, input.filters)


@customCrud_router.put("/custom/crud/update")
async def crud_update(input: CRUDUpdateInput, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Update a record in the specified table.

    <h3>Args:</h3>
        <ul>
        <li>table_name (str): The name of the table to update.</li>
        <li>data (dict): The data to update.</li>
        </ul>

    <h3>Returns:</h3>
        <ul>
        <li>JSONResponse: The JSON response containing the updated data and message.</li>
        </ul>
    """
    table_cls = TABLE_MAP.get(input.table_name)

    messages = SuccessMessages(
        client=f"{input.table_name.capitalize()} updated."
        , logger=f"Update in {input.table_name.capitalize()} was successful. Data: {input.data}"
    )

    append_user_credentials(input.data, id_user, created_by=False, updated_by=True)

    @api_output
    @db.catching(messages=messages)
    def crud__update(table_cls, data):
        return db.update(table_cls, [data])

    return crud__update(table_cls, input.data)


@customCrud_router.delete("/custom/crud/delete")
async def crud_delete(input: CRUDDeleteInput, id_user: str = Depends(validate_session)) -> APIOutput:
    """
    Delete records from a specified table based on the provided filters. Filters example:
    <pre>
    <code>
    {
        and_: {
            "id": [1, 2, 3],
            "name": ["value1", "value2"],
        },
    }
    </code>
    </pre>

    Filters accept and, or, like and not like conditions.

    <h3>Returns:</h3>
        <ul>
        <li>JSONResponse: The JSON response containing the deleted data and a message.</li>
        </ul>
    """
    table_cls = TABLE_MAP.get(input.table_name)

    messages = SuccessMessages(
        client=f"{input.table_name.capitalize()} deleted."
        , logger=f"Delete in {input.table_name.capitalize()} was successful. Filters: {input.filters}"
    )

    if isinstance(input.filters.and_, dict):
        input.filters.and_['created_by'] = [id_user]

    @api_output
    @db.catching(messages=messages)
    def crud__delete(table_cls, filters):
        return db.delete(table_cls, filters)
    
    return crud__delete(table_cls, input.filters)