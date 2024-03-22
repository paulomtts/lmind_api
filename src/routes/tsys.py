from fastapi import APIRouter, Depends

from src.start import db
from src.auth import validate_session
from src.methods import api_output, append_userstamps, append_timestamps
from src.models import TSysUsers, TSysUnits, TSysCategories, TSysNodes, TSysEdges, TProdRoutes
from src.schemas import DBOutput, SuccessMessages, WhereConditions
from src.routes.schemas import *
from src.queries import tsys_units_query

from collections import namedtuple

import os



tsys_router = APIRouter()


SELF_PATH = os.path.dirname(os.path.abspath(__file__))

# tsys_users
@tsys_router.get("/tsys/users/me")
async def get_user(id_user: str = Depends(validate_session)):
    """
    Retrieve non-sensitive user information.
    """

    @api_output
    @db.catching(messages=SuccessMessages('User retrieved!'))
    def tsys__get_user(id_user: str) -> DBOutput:
        filters = WhereConditions(and_={'google_id': [id_user]})
        user = db.query(TSysUsers, filters=filters, single=True)

        FilteredUser = namedtuple('FilteredUser', ['name', 'picture'])

        return FilteredUser(user.name, user.google_picture_url)

    return tsys__get_user(id_user)


# tsys_units
@tsys_router.post("/tsys/units/insert")
async def upsert_units(input: TSysUnitInsert, id_user: str = Depends(validate_session)):
    """
    Insert symbols and return the entire table.
    """

    data = input.unit.dict()
    append_timestamps(TSysUnits, data)
    append_userstamps(TSysUnits, data, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Unit created!'))
    def tsys__upsert_units(data: dict) -> DBOutput:

        db.insert(TSysUnits, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tsys_units_query())

    return tsys__upsert_units(data)

@tsys_router.delete("/tsys/units/delete", dependencies=[Depends(validate_session)])
async def delete_unit(input: TSysUnitDelete):
    """
    Delete symbols and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Unit deleted!'))
    def tsys__delete_unit(filters: WhereConditions) -> DBOutput:

        db.delete(TSysUnits, filters=filters)
        db.session.commit()

        return db.query(None, statement=tsys_units_query())

    return tsys__delete_unit(filters)


# tsys_categories
@tsys_router.get("/tsys/categories/insert")
async def insert_category(input: TSysCategoriesInsert, id_user: str = Depends(validate_session)):
    """
    Insert categories and return the entire table.
    """

    data = input.dict()
    append_timestamps(TSysCategories, data)
    append_userstamps(TSysCategories, data, id_user)

    @api_output
    @db.catching(messages=SuccessMessages('Category created!'))
    def tsys__insert_category(data: dict) -> DBOutput:

        db.insert(TSysCategories, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tsys_units_query())

    return tsys__insert_category(data)

@tsys_router.post("/tsys/categories/change-status")
async def update_category(input: TSysCategoriesChangeStatus, id_user: str = Depends(validate_session)):
    """
    Change category status and return the entire table.
    """

    data = input.dict()
    append_timestamps(TSysCategories, data)
    append_userstamps(TSysCategories, data, id_user)

    filters = WhereConditions(and_={'id': [data['id']]})

    @api_output
    @db.catching(messages=SuccessMessages('Category status changed!'))
    def tsys__update_category(data: dict, filters: WhereConditions) -> DBOutput:
            
            db.update(TSysCategories, data, filters=filters)
            db.session.commit()
    
            return db.query(TSysCategories)
    
    return tsys__update_category(data, filters)