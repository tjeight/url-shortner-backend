from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.services import user_signup_post
from src.dependencies.pg import get_database
from src.modules.auth.schemas import UserRegisterPostRequestModel


# Configure the user router
user_auth_router = APIRouter()


@user_auth_router.post("/signup")
async def user_signup_post_call(
    db: AsyncSession = Depends(get_database),
    payload: UserRegisterPostRequestModel = Body(...),
):
    return await user_signup_post(db=db, payload=payload)
