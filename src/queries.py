# This area is meant for complex queries made for multiple reasons: avoiding chained operations,
# reducing backend ammount of work & other reasons. This is not a rule, but a suggestion.
from collections import namedtuple

from sqlmodel import select, func, literal, case
from sqlalchemy.orm import aliased
from src.models import *

created_by_user = aliased(TSysUsers)
updated_by_user = aliased(TSysUsers)

unit_mass = aliased(TSysUnits)
unit_volume = aliased(TSysUnits)


# TSYS
def tsys_units_query(type = None):
    query =  select(
        TSysUnits.id
        , TSysUnits.name
        , TSysUnits.abbreviation
        , TSysUnits.type
        , case(
            (TSysUnits.created_by != 'system', TSysUsers.name),
            else_=TSysUnits.created_by
        ).label('created_by')
    ).outerjoin(
        TSysUsers
        , TSysUnits.created_by == TSysUsers.google_id
    ).order_by(
        TSysUnits.name
    )

    if type is not None:
        query = query.where(TSysUnits.type == type)
    
    return query
    

# TPROD
tprod_skills_query = select(
    TProdSkills.id
    , TProdSkills.name
    , TProdSkills.description
    , created_by_user.name.label('created_by')
    , TProdSkills.created_at.label('created_at')
    , updated_by_user.name.label('updated_by')
    , TProdSkills.updated_at.label('updated_at')
).outerjoin(
    created_by_user,
    TProdSkills.created_by == created_by_user.google_id
).outerjoin(
    updated_by_user,
    TProdSkills.updated_by == updated_by_user.google_id
).order_by(
    TProdSkills.name
)

tprod_resources_query = select(
    TProdResources.id
    , TProdResources.name
    , created_by_user.name.label('created_by')
    , TProdResources.created_at.label('created_at')
    , updated_by_user.name.label('updated_by')
    , TProdResources.updated_at.label('updated_at')
).outerjoin(
    created_by_user
    , TProdResources.created_by == created_by_user.google_id
).outerjoin(
    updated_by_user
    , TProdResources.updated_by == updated_by_user.google_id
).order_by(
    TProdResources.name
)

tprod_tasks_query = select(
    TProdTasks.id
    , TProdTasks.name
    , TProdTasks.description
    , TProdTasks.duration
    , TSysUnits.id.label('id_unit')
    , TSysUnits.name.label('unit')
    , TProdTasks.interruptible
    , TProdTasks.error_margin
    , created_by_user.name.label('created_by')
    , TProdTasks.created_at.label('created_at')
    , updated_by_user.name.label('updated_by')
    , TProdTasks.updated_at.label('updated_at')
).join(
    TSysUnits
    , TProdTasks.id_unit == TSysUnits.id
).outerjoin(
    created_by_user
    , TProdTasks.created_by == created_by_user.google_id
).outerjoin(
    updated_by_user
    , TProdTasks.updated_by == updated_by_user.google_id
).order_by(
    TProdTasks.name
)

tprod_products_query = select(
    TProdProducts.id
    , TProdProductTags.id.label('id_tag')
    , (
        TProdProductTags.category + \
        TProdProductTags.registry_counter + \
        TProdProductTags.subcategory
    ).label('tag')
    , TProdProducts.name
    , TProdProducts.description
    , TProdProducts.weight
    , unit_mass.id.label('id_unit_mass')
    , unit_mass.name.label('name_unit_mass')
    , TProdProducts.height
    , TProdProducts.width
    , TProdProducts.depth
    , unit_volume.id.label('id_unit_volume')
    , unit_volume.name.label('name_unit_volume')
).join(
    TProdProductTags
    , TProdProducts.id_tag == TProdProductTags.id
).join(
    unit_mass
    , TProdProducts.id_unit_mass == unit_mass.id
).join(
    unit_volume
    , TProdProducts.id_unit_volume == unit_volume.id
).order_by(
    TProdProducts.name
)


ComplexQuery = namedtuple('ComplexQuery', ['statement', 'name'])
QUERY_MAP = {
    'tsys_units': ComplexQuery(tsys_units_query, 'Units')
    , 'tprod_skills': ComplexQuery(tprod_skills_query, 'Skills')
    , 'tprod_resources': ComplexQuery(tprod_resources_query, 'Resources')
    , 'tprod_tasks': ComplexQuery(tprod_tasks_query, 'Tasks')
    , 'tprod_products': ComplexQuery(tprod_products_query, 'Products')
}