# This area is meant for complex queries made for multiple reasons: avoiding chained operations,
# reducing backend ammount of work & other reasons. This is not a rule, but a suggestion.

from sqlmodel import select, func, literal, case
from src.core.models import *


tsys_units_query = select(
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

tprod_tasks_query = select(
    TProdTasks.id
    , TProdTasks.name
    , TProdTasks.description
    , TProdTasks.duration
    , TSysUnits.name.label('unit')
    , TProdTasks.interruptible
    , TProdTasks.error_margin
).join(
    TSysUnits
    , TProdTasks.id_unit == TSysUnits.id
).order_by(
    TProdTasks.name
)