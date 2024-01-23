from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.core.auth import validate_session
from src.core.methods import api_output, append_user_credentials
from src.core.models import TSysUsers, TSysSymbols
from src.core.schemas import DBOutput, SuccessMessages, WhereConditions
from src.custom.schemas import TSysSymbolsUpsert
from src.core.start import db

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


@customConfigs_router.post("/tsys/symbols/upsert")
async def upsert_symbols(input: TSysSymbolsUpsert, id_user: str = Depends(validate_session)):
    """
    Insert or update symbols and return the entire table.
    """

    data = input.dict()

    data['created_by'] = id_user
    if not data['id']:
        data.pop('id', None)

    @api_output
    @db.catching(messages=SuccessMessages('Symbols upserted!'))
    def upsert_symbols(data: dict) -> DBOutput:

        db.upsert(TSysSymbols, [data], single=True)
        db.session.commit()

        symbols = db.query(TSysSymbols)
        users = db.query(TSysUsers)

        users = users[['name', 'google_id']]
        users = users.rename(columns={'name': 'user_name'})

        symbols = symbols.merge(users, how='left', left_on='created_by', right_on='google_id')
        symbols['created_by'] = symbols.apply(lambda row: row['created_by'] if row['created_by'] == 'system' else row['user_name'], axis=1)
        symbols = symbols.drop(columns=['user_name', 'google_id'])

        return symbols

    return upsert_symbols(data)