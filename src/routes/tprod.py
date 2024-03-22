from fastapi import APIRouter, Depends

from src.start import db
from src.auth import validate_session
from src.methods import api_output, append_userstamps, append_timestamps
from src.models import TProdSkills, TProdResources, TProdTasks, TProdResourceSkills, TSysKeywords, TProdTaskSkills, TProdProductTags, TSysNodes, TSysEdges, TProdRoutes
from src.schemas import DBOutput, SuccessMessages, WhereConditions
from src.routes.schemas import *
from src.queries import tprod_skills_query, tprod_resources_query, tprod_tasks_query

import os
import json


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

    append_timestamps(TProdSkills, data)
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

    append_timestamps(TProdResources, resource)
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

    append_timestamps(TProdTasks, task)
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


# tprod_producttags
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


# tprod_routes
@tprod_router.post("/tprod/routes/upsert")
async def upsert_routes(input: TSysRouteUpsert, id_user: str = Depends(validate_session)):
    """
    Insert nodes, edges and routes and return the entire table.
    """
    tag = input.tag.dict()
    nodes = [node.dict() for node in input.nodes]
    edges = [edge.dict() for edge in input.edges]
    routes = [route.dict() for route in input.routes_data]
    
    @api_output
    @db.catching(messages=SuccessMessages('Nodes upserted!'))
    def tprod__upsert_routes(tag: dict, nodes: list[dict], edges: list[dict], routes: list[dict]) -> DBOutput:
        
        # Upsert tag, has unique constraint on category and registry_counter
        tag['id'] = 33
        new_tag = db.upsert(TProdProductTags, data_list=[tag], single=True)

        # Prepare nodes and edges
        for nd in nodes:
            nd['id_object'] = new_tag.id
            nd['reference'] = 'tprod_producttags'
            nd['position'] = json.dumps(nd['position'])
            nd['ancestors'] = json.dumps(nd['ancestors'])
        for ed in edges:
            ed['id_object'] = new_tag.id
            ed['reference'] = 'tprod_producttags'
        for rt in routes:
            rt['id_tag'] = new_tag.id
       

        # Delete non-present nodes, edges and routes
        delete_routes = WhereConditions(
            and_={
                'id_tag': [new_tag.id]
            }
            , not_in_={
                'id_task': [rt['id_task'] for rt in routes if rt.get('id_task')]
            }
            , not_like_={
                'node_uuid': [rt['node_uuid'] for rt in routes if rt.get('node_uuid')]
            }
        )
        delete_nodes = WhereConditions(
            and_={
                'id_object': [new_tag.id]
                , 'reference': [node['reference'] for node in nodes]
            }
            , not_like_={
                'id': [nd['id'] for nd in nodes if nd.get('id')]
            }
        )
        delete_edges = WhereConditions(
            and_={
                'id_object': [new_tag.id]
                , 'reference': [edge['reference'] for edge in edges]
            }
            , not_in_={
                'id': [ed['id'] for ed in edges if ed.get('id')]
            }
        )

        db.delete(TProdRoutes, filters=delete_routes)
        db.delete(TSysNodes, filters=delete_nodes)
        db.delete(TSysEdges, filters=delete_edges)

        # Upsert nodes, edges and routes
        append_timestamps(TProdRoutes, routes)
        append_userstamps(TProdRoutes, routes, id_user)

        db.upsert(TProdRoutes, routes)

        new_nodes = db.upsert(TSysNodes, nodes)
        new_edges = db.upsert(TSysEdges, edges)

        # Parse json fields
        new_nodes['position'] = new_nodes['position'].apply(json.loads)
        new_nodes['ancestors'] = new_nodes['ancestors'].apply(json.loads)

        return {
            'tprod_producttags': new_tag
            , 'tsys_nodes': new_nodes
            , 'tsys_edges': new_edges
        }

    return tprod__upsert_routes(tag, nodes, edges, routes)