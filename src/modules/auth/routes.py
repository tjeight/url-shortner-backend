from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.services import (
    refresh_access_token_get,
    user_login_post,
    user_signup_post,
)
from src.dependencies.pg import get_database
from src.modules.auth.schemas import (
    UserAuth,
    UserLoginPostRequestModel,
    UserRegisterPostRequestModel,
)
from src.utils.auth import validate_refresh_token


# Configure the user router
user_auth_router = APIRouter(prefix="/auth")


@user_auth_router.post("/signup")
async def user_signup_post_call(
    db: AsyncSession = Depends(get_database),
    payload: UserRegisterPostRequestModel = Body(...),
):
    return await user_signup_post(db=db, payload=payload)


# Router Function to login the user
@user_auth_router.post("/login")
async def user_login_post_call(
    request: Request,
    db: AsyncSession = Depends(get_database),
    payload: UserLoginPostRequestModel = Body(...),
):
    return await user_login_post(db=db, payload=payload, request=request)


# Router to handle the refresh access token
@user_auth_router.get("/refresh/access/token")
async def refresh_access_token_get_call(
    auth: UserAuth = Depends(validate_refresh_token),
):
    return await refresh_access_token_get(auth=auth)
