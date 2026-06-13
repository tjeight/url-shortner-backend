from fastapi import APIRouter, Body, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.admin.services import (
    forgot_password_email_verification_post,
    forgot_password_otp_verification_post,
    refresh_access_token_get,
    reset_password_post,
    admin_login_post,
    admin_logout_post,
    admin_signup_post,
)
from src.dependencies.pg import get_database
from src.modules.auth.admin.schemas import (
    AdminAuth,
    AdminForgotPasswordPostRequestModel,
    AdminForgotPasswordVerifyOTPPostRequestModel,
    AdminLoginPostRequestModel,
    AdminRegisterPostRequestModel,
    AdminResetPasswordPostRequestModel,
)
from src.utils.auth import validate_admin_refresh_token


# Configure the admin router
admin_auth_router = APIRouter(prefix="/auth")


@admin_auth_router.post("/signup")
async def admin_signup_post_call(
    db: AsyncSession = Depends(get_database),
    payload: AdminRegisterPostRequestModel = Body(...),
):
    return await admin_signup_post(db=db, payload=payload)


# Router Function to login the admin
@admin_auth_router.post("/login")
async def admin_login_post_call(
    request: Request,
    db: AsyncSession = Depends(get_database),
    payload: AdminLoginPostRequestModel = Body(...),
):
    return await admin_login_post(db=db, payload=payload, request=request)


# Router to handle the refresh access token
@admin_auth_router.get("/refresh/access/token")
async def refresh_access_token_get_call(
    auth: AdminAuth = Depends(validate_admin_refresh_token),
):
    return await refresh_access_token_get(auth=auth)


# Router Function to send the forgot password email to the admin
@admin_auth_router.post("/forgot/password")
async def forgot_password_post_call(
    db: AsyncSession = Depends(get_database),
    payload: AdminForgotPasswordPostRequestModel = Body(...),
):
    return await forgot_password_email_verification_post(db=db, payload=payload)


# Router Function to verify the otp sent to the admin for password reset
@admin_auth_router.post("/forgot/password/verify/otp")
async def forgot_password_verify_otp_post_call(
    db: AsyncSession = Depends(get_database),
    payload: AdminForgotPasswordVerifyOTPPostRequestModel = Body(...),
):
    return await forgot_password_otp_verification_post(db=db, payload=payload)


# Router Function to reset the password for the admin
@admin_auth_router.post("/reset/password")
async def reset_password_post_call(
    db: AsyncSession = Depends(get_database),
    payload: AdminResetPasswordPostRequestModel = Body(...),
):
    return await reset_password_post(db=db, payload=payload)


# Router Function to handle the logout for the admin
@admin_auth_router.post("/logout")
async def admin_logout_post_call(
    db: AsyncSession = Depends(get_database),
    auth: AdminAuth = Depends(validate_admin_refresh_token),
):
    return await admin_logout_post(db=db, auth=auth)
