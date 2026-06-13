from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.services import user_login_post, user_signup_post
from src.dependencies.pg import get_database
from src.modules.auth.schemas import (
    UserLoginPostRequestModel,
    UserRegisterPostRequestModel,
)


# Configure the user router
user_auth_router = APIRouter()


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
