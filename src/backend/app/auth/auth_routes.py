# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This file is part of FMTM.
#
#     FMTM is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FMTM is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FMTM.  If not, see <https:#www.gnu.org/licenses/>.
#

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.logger import logger as log
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from ..db.db_models import DbUser
from ..db import database
from ..users import user_crud, user_schemas
from .osm import AuthUser, init_osm_auth, login_required

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/login/")
def login(user: user_schemas.UserIn, db: Session = Depends(database.get_db)):
    """
    Authenticate a user with the application.

    Args:
        user (user_schemas.UserIn): The user to authenticate.
        db (Session, optional): The database session. Injected by FastAPI.

    Returns:
        The result of verifying the user.
    """
    return user_crud.verify_user(db, user)


@router.get("/osm_login/")
def login_url(request: Request, osm_auth=Depends(init_osm_auth)):
    """
    Generate a login URL for authentication using OAuth2 Application registered with OpenStreetMap.

    Args:
        request (Request): The request object.
        osm_auth (init_osm_auth, optional): The OSM authentication object. Injected by FastAPI.

    Returns:
        A JSONResponse with the login URL.
    """
    login_url = osm_auth.login()
    log.debug(f"Login URL returned: {login_url}")
    return JSONResponse(content=login_url, status_code=200)


@router.get("/callback/")
def callback(request: Request, osm_auth=Depends(init_osm_auth)):
    """
    Perform token exchange between OpenStreetMap and Export tool API.

    Args:
        request (Request): The request object.
        osm_auth (init_osm_auth, optional): The OSM authentication object. Injected by FastAPI.

    Returns:
        A JSONResponse with the access token.
    """
    access_token = osm_auth.callback(str(request.url))
    log.debug(f"Access token returned: {access_token}")
    print(access_token, 'access_token')
    return JSONResponse(content={"access_token": access_token}, status_code=200)


@router.get("/me/", response_model=AuthUser)
def my_data(
        db: Session = Depends(database.get_db),
        user_data: AuthUser = Depends(login_required)
    ):
    """
    Retrieve user data from OSM user's API endpoint.

    Args:
        db (Session, optional): The database session. Injected by FastAPI.
        user_data (AuthUser, optional): The authenticated user data. Injected by FastAPI.

    Returns:
        A JSONResponse with the user data.
    """


    # Save user info in User table
    user = user_crud.get_user_by_id(db, user_data['id'])
    if not user:
        user_by_username = user_crud.get_user_by_username(db, user_data['username'])
        if user_by_username:
            raise HTTPException(
                status_code=400, detail=f"User with this username {user_data['username']} already exists. \
                                            Please contact the administrator for this."
            )

        db_user = DbUser(id=user_data['id'], username=user_data['username'])
        db.add(db_user)
        db.commit()


    return JSONResponse(content={"user_data": user_data}, status_code=200)
