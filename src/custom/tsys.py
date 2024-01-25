from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.core.start import db
from src.core.auth import validate_session
from src.core.methods import api_output, append_user_credentials
from src.core.models import TSysUsers, TSysUnits
from src.core.schemas import DBOutput, SuccessMessages, WhereConditions
from src.custom.schemas import TSysUnitsInsert, TSysUnitsDelete
from src.custom.queries import tsys_units_query

from collections import namedtuple

import pandas as pd
import os



customConfigs_router = APIRouter()


SELF_PATH = os.path.dirname(os.path.abspath(__file__))

@customConfigs_router.get("/tsys/users/me")
async def get_user(id_user: str = Depends(validate_session)):
    """
    Retrieve non-sensitive user information.
    """

    @api_output
    @db.catching(messages=SuccessMessages('User retrieved!'))
    def get_user(id_user: str) -> DBOutput:
        filters = WhereConditions(and_={'google_id': [id_user]})
        user = db.query(TSysUsers, filters=filters, single=True)

        FilteredUser = namedtuple('FilteredUser', ['name', 'picture'])

        return FilteredUser(user.name, user.google_picture_url)

    return get_user(id_user)


@customConfigs_router.post("/tsys/units/insert")
async def upsert_symbols(input: TSysUnitsInsert, id_user: str = Depends(validate_session)):
    """
    Insert symbols and return the entire table.
    """

    data = input.dict()
    data['created_by'] = id_user

    id = data.pop('id')
    if id:
        raise HTTPException(status_code=400, detail="Cannot provide an id during insertion. Were you trying to update?")
        
    @api_output
    @db.catching(messages=SuccessMessages('Unit created!'))
    def upsert_symbols(data: dict) -> DBOutput:

        db.insert(TSysUnits, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tsys_units_query)

    return upsert_symbols(data)

@customConfigs_router.delete("/tsys/units/delete", dependencies=[Depends(validate_session)])
async def delete_symbols(input: TSysUnitsDelete):
    """
    Delete symbols and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Unit deleted!'))
    def delete_symbols(filters: WhereConditions) -> DBOutput:

        db.delete(TSysUnits, filters=filters)
        db.session.commit()

        return db.query(None, statement=tsys_units_query)

    return delete_symbols(filters)