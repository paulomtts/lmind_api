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

class UserFields(SQLModel):
    created_by: str = Field(regex=REGEX_NUMBERS)
    updated_by: str = Field(regex=REGEX_NUMBERS)
    

class Users(TimestampModel, table=True):
    __tablename__ = 'users'

    google_id: Optional[str] = Field(default=None, regex=REGEX_NUMBERS, primary_key=True)
    google_email: str = Field(regex=EMAIL_REGEX)
    google_picture_url: str = Field(regex=URL_REGEX)
    google_access_token: str
    name: str = Field(regex=REGEX_WORDS)
    locale: str = Field(regex=REGEX_WORDS)

class Sessions(TimestampModel, table=True):
    __tablename__ = 'sessions'

    id: Optional[int] = Field(default=None, primary_key=True)
    google_id: str = Field(foreign_key='users.google_id', regex=REGEX_NUMBERS)
    token: str = Field(regex=REGEX_SHA256)
    user_agent: str = Field(regex=REGEX_SHA256)
    client_ip: str = Field(regex=REGEX_IP)

class Categories(TimestampModel, UserFields, table=True):
    __tablename__ = 'categories'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    type: str = Field(regex=REGEX_WORDS)

class Units(TimestampModel, UserFields, table=True):
    __tablename__ = 'units'

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(regex=REGEX_WORDS)
    abbreviation: str = Field(regex=REGEX_WORDS)
    base: int