from fastapi import APIRouter, Depends

from src.schemas import DBOutput, APIOutput, CRUDSelectInput, CRUDDeleteInput, CRUDInsertInput, CRUDUpdateInput, SuccessMessages
from src.methods import api_output, append_userstamps, append_timestamps
from src.auth import validate_session
from src.start import db
from src.models import TABLE_MAP, SimpleQuery
from src.queries import QUERY_MAP


crud_router = APIRouter()


@crud_router.post("/crud/insert")
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

    append_timestamps(input.data)
    append_userstamps(input.data, id_user)
    
    @api_output
    @db.catching(messages=messages)
    def crud__insert(table_cls, data) -> DBOutput:
        return db.insert(table_cls, data)
    
    return crud__insert(table_cls, input.data)


@crud_router.post("/crud/select", dependencies=[Depends(validate_session)])
async def crud_select(input: CRUDSelectInput) -> APIOutput:
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

    simple_query = TABLE_MAP.get(input.table_name) or SimpleQuery(name=input.table_name, cls=None)
    complex_query = QUERY_MAP.get(input.table_name)
    
    statement = None
    if complex_query:
        if not callable(complex_query.statement):
            statement = complex_query.statement
        else:
            statement = complex_query.statement(**input.lambda_kwargs)

    messages = SuccessMessages(
        client=f"{simple_query.name} retrieved." if simple_query.cls else f"{complex_query.name} retrieved."
        , logger=f"Querying <{input.table_name}> was succesful! Filters: {input.filters}"
    )

    @api_output
    @db.catching(messages=messages)
    def crud__select(table_cls, statement, filters):
        return db.query(table_cls=table_cls, statement=statement, filters=filters)

    return crud__select(simple_query.cls, statement, input.filters)


@crud_router.put("/crud/update")
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

    append_userstamps(input.data, id_user, created_by=False, updated_by=True)

    @api_output
    @db.catching(messages=messages)
    def crud__update(table_cls, data):
        return db.update(table_cls, [data])

    return crud__update(table_cls, input.data)


@crud_router.delete("/crud/delete", dependencies=[Depends(validate_session)])
async def crud_delete(input: CRUDDeleteInput) -> APIOutput:
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

    input.filters.not_like_['created_by'] = ['system'] # reason: system created data should not be deleted

    @api_output
    @db.catching(messages=messages)
    def crud__delete(table_cls, filters):
        return db.delete(table_cls, filters)
    
    return crud__delete(table_cls, input.filters)