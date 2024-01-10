from fastapi import APIRouter, HTTPException, Request, Response, Cookie, Query, Depends
from fastapi.responses import RedirectResponse, JSONResponse

from src.core.start import db
from src.core.models import Users, Sessions
from src.core.schemas import SuccessMessages, DBOutput, WhereConditions
from src.core.security import generate_session_token, hash_plaintext, generate_jwt, decode_jwt

from typing import Annotated

import requests
import base64
import json
import os


auth_router = APIRouter()


# Session tokens are JWTs built and encoded with a specific public key
# that is never shared with the client. The client cannot decode the 
# session JWT. The client can only send the JWT to the server for
# verification. This is to prevent the client from tampering with the
# session JWT.

# The server can decode the session JWT and verify the payload. If the
# payload is valid, the server can then verify the user's identity and
# allow the user to access the protected route.

############# DEVELOPMENT ONLY #############
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
FRONTEND_REDIRECT_URI = os.getenv('FRONTEND_REDIRECT_URL')
############# DEVELOPMENT ONLY #############

class MissingSessionError(BaseException):
    """
    An exception raised when a session token could be decrypted 
    but no session could be found matching its contents. This
    could be an indication that the session token was stolen.
    """


def validate_session(response: Response, request: Request, cbk_s: Annotated[str | None, Cookie()]):
    """
    Validate the session cookie. If the cookie is valid, extend the expiration,
    otherwise, delete the cookie.
    """
    try:
        session_cookie = cbk_s.encode('utf-8')

        hashed_user_agent = hash_plaintext(json.dumps(request.headers.get("User-Agent")))
        hashed_user_agent = base64.b64encode(hashed_user_agent).decode('utf-8')

        decoded_token: dict = decode_jwt(session_cookie)
        client_ip = request.client.host

        if hashed_user_agent != decoded_token.get("user_agent") or client_ip != decoded_token.get("client_ip"):
            raise ValueError("Session data did not match preliminary client data.")


        @db.catching(SuccessMessages(client="Session validated."))
        def auth__validate_session(decoded_token: dict, user_agent: dict, client_ip: str):
            session_data = {
                'google_id': [decoded_token.get("google_id")]
                , 'token': [decoded_token.get("token")]
                , 'user_agent': [user_agent]
                , 'client_ip': [client_ip]
            }

            filters = WhereConditions(and_=session_data)
            session = db.query(Sessions, filters=filters, single=True)

            if session:
                return True
            else:
                return False

        is_valid_session, _, _ = auth__validate_session(decoded_token, hashed_user_agent, client_ip)

        if not is_valid_session:
            db.logger.error("Session token belonged to us, but no session matched it's data. Was this cookie stolen?")
            raise MissingSessionError("No session could be found matching the provided session token.")
        
        return decoded_token.get("google_id")

    except Exception as e:
        db.logger.error(f"An error occurred while validating a session: \n{e}")
        response.delete_cookie(key="cbk_s")
        raise HTTPException(status_code=401, detail="Unauthorized access.", headers=response.headers)


# Routes
@auth_router.get("/auth/login")
async def auth_login():
    """
    Build the Google OAuth2 login URL and redirect the user to it.
    """
    return JSONResponse(content={'url': f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"}, status_code=200)


@auth_router.get("/auth/callback")
async def auth_callback(request: Request, code: str = Query(...)):
    """
    Build a session for the user. This is the callback URL that Google will
    redirect the user to after they have successfully authenticated.
    """

    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:

        access_token = response.json().get("access_token")
        if access_token:
            user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})

            # 1) collect information
            hashed_user_agent = hash_plaintext(json.dumps(request.headers.get("User-Agent")))
            hashed_user_agent = base64.b64encode(hashed_user_agent).decode('utf-8')

            client_ip = request.client.host
            user_info: dict = user_info.json()
            session_token = generate_session_token()


            # 2) build user & session data
            user_data = {
                'google_id': user_info.get("id")
                , 'google_email': user_info.get("email")
                , 'google_picture_url': user_info.get("picture")
                , 'google_access_token': access_token
                , 'name': user_info.get("name")
                , 'locale': user_info.get("locale")
            }

            session_data = {
                'google_id': user_info.get("id")
                , 'token': session_token
                , 'user_agent': hashed_user_agent
                , 'client_ip': client_ip
            }

            # 3) build payload & generate JWT
            payload = {
                "google_id": user_info.get("id")
                , "token": session_token
                , "user_agent": hashed_user_agent
                , "client_ip": client_ip
            }

            jwt_token = generate_jwt(payload)

            @db.catching(SuccessMessages(client="User was successfully authenticated.", logger="User authenticated. Session initiated."))
            def auth__initiate_session(user_data, session_data):
                
                user = db.upsert(Users, [user_data], single=True)
                if user:
                    db.upsert(Sessions, [session_data])

                return []
            
            db_output: DBOutput = auth__initiate_session(user_data, session_data)

            if 200 <= response.status_code < 300:
                response = RedirectResponse(url=f"{FRONTEND_REDIRECT_URI}", headers=request.headers)
                response.set_cookie(key="cbk_s", value=jwt_token, httponly=True, samesite='none', secure=True, expires=(60 * 60 * 24 * 7))
                return response

            raise HTTPException(status_code=db_output.status, detail=db_output.message)
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    raise HTTPException(status_code=401, detail="Bad request.")


@auth_router.get('/auth/validate', dependencies=[Depends(validate_session)])
async def auth_validate():
    return JSONResponse(status_code=200, content={"message": "Session is valid."})


@auth_router.get('/auth/logout')
async def auth_logout(response: Response):
    response.delete_cookie(key="cbk_s", httponly=True, samesite='none', secure=True)
    return JSONResponse(status_code=200, content={"message": "Session has been terminated."}, headers=response.headers)