from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.auth.services import (
    forgot_password_email_verification_post,
    forgot_password_otp_verification_post,
    refresh_access_token_get,
    reset_password_post,
    user_login_post,
    user_logout_post,
    user_signup_post,
)
from src.dependencies.pg import get_database
from src.modules.auth.schemas import (
    UserAuth,
    UserForgotPasswordPostRequestModel,
    UserForgotPasswordVerifyOTPPostRequestModel,
    UserLoginPostRequestModel,
    UserRegisterPostRequestModel,
    UserResetPasswordPostRequestModel,
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


# Router Function to send the add the forgot password email to the user
@user_auth_router.post("/forgot/password")
async def forgot_password_post_call(
    db: AsyncSession = Depends(get_database),
    payload: UserForgotPasswordPostRequestModel = Body(...),
):
    return await forgot_password_email_verification_post(db=db, payload=payload)


# Router Function to verify the otp sent to the user for password reset
@user_auth_router.post("/forgot/password/verify/otp")
async def forgot_password_verify_otp_post_call(
    db: AsyncSession = Depends(get_database),
    payload: UserForgotPasswordVerifyOTPPostRequestModel = Body(...),
):
    return await forgot_password_otp_verification_post(db=db, payload=payload)


# Router Function to reset the password for the user
@user_auth_router.post("/reset/password")
async def reset_password_post_call(
    db: AsyncSession = Depends(get_database),
    payload: UserResetPasswordPostRequestModel = Body(...),
):
    return await reset_password_post(db=db, payload=payload)


# Router Function to handle the logout for the user
@user_auth_router.post("/logout")
async def user_logout_post_call(
    db: AsyncSession = Depends(get_database),
    auth: UserAuth = Depends(validate_refresh_token),
):
    return await user_logout_post(db=db, auth=auth)
