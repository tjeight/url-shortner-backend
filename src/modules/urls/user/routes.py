from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.urls.user.services import (
    url_short_get,
    url_short_post,
    user_url_delete,
    url_redirect_get,
    user_url_refresh,
)
from src.modules.auth.user.schemas import UserAuth
from src.dependencies.pg import get_database

from src.modules.urls.user.schemas import (
    UserURLDeleteRequestModel,
    UserURLPostRequestModel,
    UserURLRefreshRequestModel,
)
from src.utils.auth import validate_user_auth

# Configure the user url router
user_url_router = APIRouter(prefix="/urls", tags=["User URLs"])


# Router function to handle the user url post
@user_url_router.post("/short")
async def url_short_post_call(
    db: AsyncSession = Depends(get_database),
    auth: UserAuth = Depends(validate_user_auth),
    payload: UserURLPostRequestModel = Body(...),
):
    return await url_short_post(db=db, payload=payload, auth=auth)


# Router Function to handle the user url get
@user_url_router.get("/all")
async def url_short_get_call(
    db: AsyncSession = Depends(get_database),
    auth: UserAuth = Depends(validate_user_auth),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    return await url_short_get(
        db=db,
        auth=auth,
        page=page,
        size=size,
    )


@user_url_router.delete("/short")
async def url_short_delete_call(
    db: AsyncSession = Depends(get_database),
    payload: UserURLDeleteRequestModel = Body(...),
    auth: UserAuth = Depends(validate_user_auth),
):
    return await user_url_delete(
        db=db,
        payload=payload,
        auth=auth,
    )


# Router Function to handle the redirect url get
@user_url_router.get("/redirect/{short_code}")
async def url_redirect_call(
    short_code: str,
    db: AsyncSession = Depends(get_database),
):

    return await url_redirect_get(
        db=db,
        short_code=short_code,
    )


# Router Function to handle the refresh the url
@user_url_router.post("/refresh")
async def url_refresh_call(
    db: AsyncSession = Depends(get_database),
    auth: UserAuth = Depends(validate_user_auth),
    payload: UserURLRefreshRequestModel = Body(...),
):
    return await user_url_refresh(
        db=db,
        auth=auth,
        payload=payload,
    )
