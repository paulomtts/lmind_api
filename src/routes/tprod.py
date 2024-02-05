from fastapi import APIRouter, Depends

from src.start import db
from src.auth import validate_session
from src.methods import api_output, append_userstamps, append_timestamps
from src.models import TProdSkills, TProdResources, TProdTasks
from src.schemas import DBOutput, SuccessMessages, WhereConditions
from src.routes.schemas import *
from src.queries import tprod_skills_query, tprod_resources_query, tprod_tasks_query

import os



tprod_router = APIRouter()


SELF_PATH = os.path.dirname(os.path.abspath(__file__))


# tprod_skills 
@tprod_router.post("/tprod/skills/upsert")
async def upsert_skills(input: TProdSkillUpsert, id_user: str = Depends(validate_session)):
    """
    Insert skills and return the entire table.
    """

    data = input.dict()
    if not data.get('id'): data.pop('id')

    append_timestamps(data)
    append_userstamps(data, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Skill created!'))
    def tprod__upsert_skills(data: dict) -> DBOutput:

        db.upsert(TProdSkills, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tprod_skills_query)

    return tprod__upsert_skills(data)

@tprod_router.delete("/tprod/skills/delete", dependencies=[Depends(validate_session)])
async def delete_skills(input: TProdSkillDelete):
    """
    Delete skills and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Skill deleted!'))
    def tprod__delete_skills(filters: WhereConditions) -> DBOutput:

        db.delete(TProdSkills, filters=filters)
        db.session.commit()

        return db.query(None, statement=tprod_skills_query)

    return tprod__delete_skills(filters)


# tprod_resources
@tprod_router.post("/tprod/resources/upsert")
async def upsert_resources(input: TProdResourceUpsert, id_user: str = Depends(validate_session)):
    """
    Insert resources and return the entire table.
    """

    data = input.dict()
    if not data.get('id'): data.pop('id')

    append_timestamps(data)
    append_userstamps(data, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Resource created!'))
    def tprod__upsert_resources(data: dict) -> DBOutput:

        db.upsert(TProdResources, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tprod_resources_query)

    return tprod__upsert_resources(data)

@tprod_router.delete("/tprod/resources/delete", dependencies=[Depends(validate_session)])
async def delete_resources(input: TProdResourceDelete):
    """
    Delete resources and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Resource deleted!'))
    def tprod__delete_resources(filters: WhereConditions) -> DBOutput:

        db.delete(TProdResources, filters=filters)
        db.session.commit()

        return db.query(None, statement=tprod_resources_query)

    return tprod__delete_resources(filters)


# tprod_tasks
@tprod_router.post("/tprod/tasks/upsert")
async def upsert_tasks(input: TProdTaskUpsert, id_user: str = Depends(validate_session)):
    """
    Insert tasks and return the entire table.
    """

    data = input.dict()
    if not data.get('id'): data.pop('id')

    append_timestamps(data)
    append_userstamps(data, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Task created!'))
    def tprod__upsert_tasks(data: dict) -> DBOutput:

        db.upsert(TProdTasks, [data], single=True)
        db.session.commit()

        return db.query(None, statement=tprod_tasks_query)

    return tprod__upsert_tasks(data)

@tprod_router.delete("/tprod/tasks/delete", dependencies=[Depends(validate_session)])
async def delete_tasks(input: TProdTaskDelete):
    """
    Delete tasks and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Task deleted!'))
    def tprod__delete_tasks(filters: WhereConditions) -> DBOutput:

        db.delete(TProdTasks, filters=filters)
        db.session.commit()

        return db.query(None, statement=tprod_tasks_query)

    return tprod__delete_tasks(filters)