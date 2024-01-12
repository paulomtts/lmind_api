from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse

from src.core.auth import validate_session
from src.core.methods import api_output
from src.core.models import TSysUsers
from src.core.schemas import DBOutput, SuccessMessages, WhereConditions

from src.core.start import db
from collections import namedtuple
import os


customConfigs_router = APIRouter()


SELF_PATH = os.path.dirname(os.path.abspath(__file__))

@customConfigs_router.get("/custom/configs/maps")
async def get_maps(request: Request):
    """
    Obtain the maps.json file.

    <h3>Returns:</h3>
        <ul>
        <li>JSONResponse: The JSON response containing the json.</li>
        </ul>
    """

    try:
        with open(f"{SELF_PATH}/maps.json", "r") as f:
            json_data = f.read()

        db.logger.info(f"Successfully loaded maps.json file.")
    except Exception as e:
        db.logger.error(f"Could not load maps.json file. Error: {e}")
        json_data = {}

    return JSONResponse(status_code=200, content={'data': json_data, 'message': 'Configs retrieved!'}, headers=request.headers)

@customConfigs_router.get("/custom/configs/user")
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