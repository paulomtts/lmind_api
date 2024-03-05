from fastapi import APIRouter, Depends

from src.start import db
from src.auth import validate_session
from src.methods import api_output, append_userstamps, append_timestamps
from src.models import TProdSkills, TProdResources, TProdTasks, TProdResourceSkills, TSysKeywords, TProdTaskSkills, TProdProductTags
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
    append_userstamps(TProdSkills, data, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Skill created!'))
    def tprod__upsert_skills(data: dict) -> DBOutput:

        db.upsert(TProdSkills, [data])
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

    resource = input.resource.dict()
    keyword_list = input.keyword_list
    id_skill_list = input.id_skill_list
    
    if not resource.get('id'): resource.pop('id', None)

    append_timestamps(resource)
    append_userstamps(TProdResources, resource, id_user)

    @api_output
    @db.catching(messages=SuccessMessages('Resource operation successful!'))
    def tprod__upsert_resources(resource: dict, keyword_list: list[str], id_skill_list: list[int]) -> DBOutput:
        resource_returning = db.upsert(TProdResources, [resource], single=True)

        id_resource = resource_returning.id

        if resource.get('id'): # reason: differs between an UPDATE or INSERT
            skills_delete_filters = WhereConditions(and_={'id_resource': [resource['id']]}, not_like={'id_skill': id_skill_list})
            db.delete(TProdResourceSkills, filters=skills_delete_filters)

            keywords_delete_filters = WhereConditions(and_={'id_object': [resource['id']], 'reference': ['tprod_resources']}, not_like={'keyword': keyword_list})
            db.delete(TSysKeywords, filters=keywords_delete_filters)

        db.upsert(TSysKeywords, [{'id_object': id_resource, 'reference': 'tprod_resources', 'keyword': keyword} for keyword in keyword_list]) 

        db.upsert(TProdResourceSkills, [{'id_resource': id_resource, 'id_skill': id_skill} for id_skill in id_skill_list])
        db.session.commit()
        return db.query(None, statement=tprod_resources_query)
    
    return tprod__upsert_resources(resource, keyword_list, id_skill_list)

@tprod_router.delete("/tprod/resources/delete", dependencies=[Depends(validate_session)])
async def delete_resources(input: TProdResourceDelete):
    """
    Delete resources and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Resource deleted!'))
    def tprod__delete_resources(filters: WhereConditions) -> DBOutput:

        db.delete(TProdResourceSkills, filters=WhereConditions(and_={'id_resource': [input.id]}))
        db.delete(TSysKeywords, filters=WhereConditions(and_={'id_object': [input.id], 'reference': ['tprod_resources']}))
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

    task = input.task.dict()
    keyword_list = input.keyword_list
    id_skill_list = input.id_skill_list

    if not task.get('id'): task.pop('id')

    append_timestamps(task)
    append_userstamps(TProdTasks, task, id_user)
        
    @api_output
    @db.catching(messages=SuccessMessages('Task operation successful!'))
    def tprod__upsert_tasks(task: dict, keyword_list: list[str], id_skill_list: list[int]) -> DBOutput:
        task_returning = db.upsert(TProdTasks, [task], single=True)

        id_task = task_returning.id

        if task.get('id'): # reason: differs between an UPDATE or INSERT
            skills_delete_filters = WhereConditions(and_={'id_task': [task['id']]}, not_like={'id_skill': id_skill_list})
            db.delete(TProdTaskSkills, filters=skills_delete_filters)

            keywords_delete_filters = WhereConditions(and_={'id_object': [task['id']], 'reference': ['tprod_tasks']}, not_like={'keyword': keyword_list})
            db.delete(TSysKeywords, filters=keywords_delete_filters)

        db.upsert(TSysKeywords, [{'id_object': id_task, 'reference': 'tprod_tasks', 'keyword': keyword} for keyword in keyword_list])
        db.upsert(TProdTaskSkills, [{'id_task': id_task, 'id_skill': id_skill} for id_skill in id_skill_list])
        db.session.commit()

        return db.query(None, statement=tprod_tasks_query)

    return tprod__upsert_tasks(task, keyword_list, id_skill_list)

@tprod_router.delete("/tprod/tasks/delete", dependencies=[Depends(validate_session)])
async def delete_tasks(input: TProdTaskDelete):
    """
    Delete tasks and return the entire table.
    """

    filters = WhereConditions(and_={'id': [input.id]})

    @api_output
    @db.catching(messages=SuccessMessages('Task deleted!'))
    def tprod__delete_tasks(filters: WhereConditions) -> DBOutput:

        db.delete(TProdTaskSkills, filters=WhereConditions(and_={'id_task': [input.id]}))
        db.delete(TSysKeywords, filters=WhereConditions(and_={'id_object': [input.id], 'reference': ['tprod_tasks']}))
        db.delete(TProdTasks, filters=filters)
        db.session.commit()

        return db.query(None, statement=tprod_tasks_query)

    return tprod__delete_tasks(filters)



@tprod_router.post("/tprod/products/tag-check-availability", dependencies=[Depends(validate_session)])
async def product_tag_check_availability(input: TProdProductTagCheckAvailability):
    """
    Check the availability of a product tag.
    """

    filters = WhereConditions(and_={'category': [input.category]})

    @api_output
    @db.catching(messages=SuccessMessages('Product tag is available!'))
    def tprod__product_tag_check_availability(filters: WhereConditions) -> DBOutput:

        returning_df = db.query(TProdProductTags, statement=None, filters=filters)
        is_available = input.registry_counter not in returning_df['registry_counter'].tolist()

        if not is_available:
            highest_registry_counter = int(returning_df['registry_counter'].max() or 0)

            return {
                'object': {
                    'category': input.category
                    , 'registry_counter': highest_registry_counter + 1
                }
                , 'available': False
                , 'message': f' product tag is not available. Returned a suggestion.'
            }
        
        return {'available': True, 'message': ''}
    return tprod__product_tag_check_availability(filters)

    