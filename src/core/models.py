from sqlmodel import Field, SQLModel
from datetime import datetime
from typing import Optional

REGEX_SHA256 = r'^[a-fA-F0-9]{64}$'
REGEX_NUMBERS = r'^[0-9]+$'
REGEX_WORDS = r'^[a-zA-Z\s]+$'
REGEX_IP = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
URL_REGEX = r'^https:\/\/[^\s\/$.?#].[^\s]*$'
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


class TimestampModel(SQLModel):
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    # Note: sqalchemy's .on_conflict_do_update() does not trigger onupdate events 
    # see the post at https://github.com/sqlalchemy/sqlalchemy/discussions/5903#discussioncomment-327672

class UserstampModel(SQLModel):
    created_by: str = Field(regex=REGEX_NUMBERS)
    updated_by: str = Field(regex=REGEX_NUMBERS)
    

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
    google_access_token: str
    name: str = Field(regex=REGEX_WORDS)
    locale: str = Field(regex=REGEX_WORDS)

class TSysSessions(TimestampModel, table=True):
    __tablename__ = 'tsys_sessions'

    google_id: Optional[str] = Field(default=None, regex=REGEX_NUMBERS, primary_key=True)
    id_role: Optional[int] = Field(foreign_key='tsys_roles.id')
    token: str = Field(regex=REGEX_SHA256)
    user_agent: str = Field(regex=REGEX_SHA256)
    client_ip: str = Field(regex=REGEX_IP)

class TSysSymbols(SQLModel, table=True):
    __tablename__ = 'tsys_symbols'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    abbreviation: str = Field(regex=REGEX_WORDS)
    base: int = Field(default=1)
    type: str = Field(regex=REGEX_WORDS)
    created_by: str = Field(regex=REGEX_WORDS)
