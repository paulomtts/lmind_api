from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional, Literal
from collections import namedtuple


REGEX_SHA256 = r'^[a-fA-F0-9]{64}$'
REGEX_UUID4 = r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$'
REGEX_NUMBERS = r'^[0-9]+$'
REGEX_WORDS = r"^[a-zA-Z\s]+$"
REGEX_IP = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
URL_REGEX = r'^https:\/\/[^\s\/$.?#].[^\s]*$'
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


class TimestampModel(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # Note: sqalchemy's .on_conflict_do_update() does not trigger onupdate events 
    # see the post at https://github.com/sqlalchemy/sqlalchemy/discussions/5903#discussioncomment-327672

class UserstampModel(SQLModel):
    created_by: Optional[str] = Field(regex=REGEX_NUMBERS)
    updated_by: Optional[str] = Field(regex=REGEX_NUMBERS)
    

# TSYS
class TSysRoles(SQLModel, table=True):
    __tablename__ = 'tsys_roles'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(regex=EMAIL_REGEX)
    role: str = Field(regex=REGEX_WORDS)
    level: int = Field(default=1)

class TSysUsers(TimestampModel, table=True):
    __tablename__ = 'tsys_users'

    id_role: Optional[int] = Field(foreign_key='tsys_roles.id', primary_key=True)
    google_id: Optional[str] = Field(default=None, regex=REGEX_NUMBERS)
    google_email: str = Field(regex=EMAIL_REGEX)
    google_picture_url: str = Field(regex=URL_REGEX)
    google_access_token: str = Field(...)
    name: str = Field(regex=REGEX_WORDS)
    locale: str = Field(regex=REGEX_WORDS)

class TSysSessions(TimestampModel, table=True):
    __tablename__ = 'tsys_sessions'

    google_id: Optional[str] = Field(default=None, regex=REGEX_NUMBERS, primary_key=True)
    id_role: Optional[int] = Field(foreign_key='tsys_roles.id')
    token: str = Field(regex=REGEX_SHA256)
    user_agent: str = Field(regex=REGEX_SHA256)
    client_ip: str = Field(regex=REGEX_IP)

class TSysUnits(SQLModel, table=True):
    __tablename__ = 'tsys_units'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    abbreviation: str = Field(regex=REGEX_WORDS)
    type: str = Field(regex=REGEX_WORDS)
    created_by: str = Field(regex=REGEX_WORDS)
    
class TSysCategories(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tsys_categories'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    description: str = Field(regex=REGEX_WORDS)
    reference: str = Field(regex=REGEX_WORDS)
    status: bool = Field(default=True)
    
class TSysKeywords(SQLModel, table=True):
    __tablename__ = 'tsys_keywords'

    id_object: int = Field(primary_key=True)
    reference: str = Field(regex=REGEX_WORDS, primary_key=True)
    keyword: str = Field(regex=REGEX_WORDS, primary_key=True)


# TPROD   
class TProdResources(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tprod_resources'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)

class TProdSkills(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tprod_skills'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    description: str = Field(regex=REGEX_WORDS)

class TProdTasks(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tprod_tasks'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    description: str = Field(regex=REGEX_WORDS)
    duration: float = Field(default=0.0)
    id_unit: int = Field(foreign_key='tsys_units.id')
    interruptible: bool = Field(default=False)
    error_margin: float = Field(default=0.0)

class TProdTaskSkills(SQLModel, table=True):
    __tablename__ = 'tprod_taskskills'

    id_task: int = Field(foreign_key='tprod_tasks.id', primary_key=True)
    id_skill: int = Field(foreign_key='tprod_skills.id', primary_key=True)

class TProdResourceSkills(SQLModel, table=True):
    __tablename__ = 'tprod_resourceskills'

    id_resource: int = Field(foreign_key='tprod_resources.id', primary_key=True)
    id_skill: int = Field(foreign_key='tprod_skills.id', primary_key=True)
    
class TProdProductTags(SQLModel, table=True):
    __tablename__ = 'tprod_producttags'

    id: Optional[int] = Field(default=None, primary_key=True)
    category: str = Field(regex=REGEX_WORDS)
    registry_counter: int = Field(default=0)
    produced_counter: int = Field(default=0)
    subcategory: str = Field(regex=REGEX_WORDS)

class TProdProducts(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tprod_products'

    id: Optional[int] = Field(default=None, primary_key=True)
    id_tag: int = Field(foreign_key='tprod_producttags.id')
    name: str = Field(regex=REGEX_WORDS)
    description: str = Field(regex=REGEX_WORDS)
    weight: float = Field(default=0.0)
    id_unit_mass: int = Field(foreign_key='tsys_units.id')
    height: float = Field(default=0.0)
    width: float = Field(default=0.0)
    depth: float = Field(default=0.0)
    id_unit_volume: int = Field(foreign_key='tsys_units.id') 

class TProdRoutes(TimestampModel, UserstampModel, table=True):
    __tablename__ = 'tprod_routes'

    id: Optional[int] = Field(default=None, primary_key=True)
    id_tag: int = Field(foreign_key='tprod_producttags.id')
    id_task: int = Field(foreign_key='tprod_tasks.id')
    node_uid: str = Field(regex=REGEX_UUID4)
    node_level: int = Field(default=0)
    node_quantity: int = Field(default=1)


SimpleQuery = namedtuple('SimpleQuery', ['name', 'cls'])
TABLE_MAP = {
    'tsys_categories': SimpleQuery("Categories", TSysCategories)
    , 'tsys_keywords': SimpleQuery("Keywords", TSysKeywords)

    , 'tprod_resourceskills': SimpleQuery("Resource's skills", TProdResourceSkills)
    , 'tprod_taskskills': SimpleQuery("Task's skills", TProdTaskSkills)
    , 'tprod_routes': SimpleQuery("Routes", TProdRoutes)
    , 'tprod_producttags': SimpleQuery("Product's tags", TProdProductTags)
}