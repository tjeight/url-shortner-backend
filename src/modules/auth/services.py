import logging
from time import perf_counter

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.redis import redis_client
from src.configs.settings import settings
from src.modules.auth.enums import TokenType, UserRole
from src.modules.auth.helpers import build_otp_email
from src.modules.auth.models import Users, UserSession

# Set the logger
from src.modules.auth.schemas import (
    UserAuth,
    UserForgotPasswordPostRequestModel,
    UserForgotPasswordVerifyOTPPostRequestModel,
    UserLoginPostRequestModel,
    UserRegisterPostRequestModel,
    UserResetPasswordPostRequestModel,
)
from src.utils.auth import (
    create_jwt_token,
    get_client_info,
    hash_password,
    hash_refresh_token,
    validate_password_reset_token,
    verify_hashed_password,
)
from src.utils.email import send_email
from src.utils.generators import generate_otp

logger = logging.getLogger(__name__)


# Function to register the user
async def user_signup_post(
    db: AsyncSession, payload: UserRegisterPostRequestModel
) -> JSONResponse:
    try:
        # Check if the email exists
        email_fetch_query = await db.execute(
            select(Users).where(Users.user_email == payload.user_email)
        )

        email_result = email_fetch_query.scalar_one_or_none()

        # Check if the email exists
        if email_result:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Email Already Exists"},
            )

        # Create the hash password
        hashed_password = hash_password(payload.password)

        # Create the user
        new_user = Users(
            user_email=payload.user_email,
            first_name=payload.first_name,
            last_name=payload.last_name,
            password_hash=hashed_password,
            role=UserRole.USER.value,
        )

        # Add the new user to the database
        db.add(new_user)

        # Commit the changes to the database
        await db.commit()

        # Return the success response
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"success": True, "message": "User Registered Successfully"},
        )

    except Exception:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# User Function to post the login
async def user_login_post(
    db: AsyncSession, payload: UserLoginPostRequestModel, request: Request
) -> JSONResponse:
    try:
        start_time = perf_counter()
        # Fetch user
        result = await db.execute(
            select(Users).where(Users.user_email == payload.user_email)
        )
        user = result.scalar_one_or_none()

        print(f"DB Query Time: {perf_counter() - start_time:.4f} seconds")

        start_time = perf_counter()
        #  Don't reveal which field is wrong
        if not user or not verify_hashed_password(user.password_hash, payload.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid email or password"},
            )

        print(f"Password Verification Time: {perf_counter() - start_time:.4f} seconds")

        start_time = perf_counter()
        # Get client info
        ip_address, device_info = get_client_info(request=request)

        print(f"Client Info Extraction Time: {perf_counter() - start_time:.4f} seconds")

        start_time = perf_counter()
        # Create session
        new_session = UserSession(
            user_id=user.user_id,
            device_info=device_info,
            ip_address=ip_address,
        )
        db.add(new_session)  # add to DB
        await db.flush()  # get session_id before token
        print(f"Session Creation Time: {perf_counter() - start_time:.4f} seconds")

        start_time = perf_counter()
        # Build token payload
        access_token_payload = {
            "user_id": str(user.user_id),
            "role": user.role,
            "session_id": str(new_session.user_session_id),
            "type": TokenType.ACCESS_TOKEN.value,
        }

        refresh_token_payload = {
            "user_id": str(user.user_id),
            "role": user.role,
            "session_id": str(new_session.user_session_id),
            "type": TokenType.REFRESH_TOKEN.value,
        }

        # Create tokens
        access_token = await create_jwt_token(
            access_token_payload, TokenType.ACCESS_TOKEN
        )
        refresh_token = await create_jwt_token(
            refresh_token_payload, TokenType.REFRESH_TOKEN
        )
        print(f"Token Creation Time: {perf_counter() - start_time:.4f} seconds")

        start_time = perf_counter()
        # Create the hash of the refresh token
        refresh_token_hash = hash_refresh_token(refresh_token)

        # Store it in the session

        new_session.refresh_token_hash = refresh_token_hash

        await db.commit()  #  persist session

        print(f"Session Persistence Time: {perf_counter() - start_time:.4f} seconds")

        access_token_cookie_expiry_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_token_cookie_expiry_time = (
            settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        # Build response
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Logged in successfully"},
        )

        #  Set both cookies properly
        response.set_cookie(
            key=TokenType.ACCESS_TOKEN.value,
            value=access_token,
            max_age=access_token_cookie_expiry_time,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        response.set_cookie(
            key=TokenType.REFRESH_TOKEN.value,
            value=refresh_token,
            max_age=refresh_token_cookie_expiry_time,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return response

    except Exception as e:
        await db.rollback()
        logger.error(f"Login error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function to handle the refresh access token
async def refresh_access_token_get(auth: UserAuth):
    try:
        # Create the access token since the refresh token is already verified
        # Build token payload
        access_token_payload = {
            "user_id": str(auth.user_id),
            "role": auth.role,
            "session_id": str(auth.session_id),
            "type": TokenType.ACCESS_TOKEN.value,
        }

        # Create the access token
        access_token = await create_jwt_token(
            payload=access_token_payload, token_type=TokenType.ACCESS_TOKEN
        )

        # Create the expiry time for the cookie
        access_token_expiry_time = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        # Create the response and set the cookie
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Access Token Refreshed Successfully",
            },
        )

        response.set_cookie(
            key=TokenType.ACCESS_TOKEN.value,
            value=access_token,
            httponly=True,
            path="/",
            samesite="lax",
            secure=True,
            max_age=access_token_expiry_time,
        )

        return response

    except Exception as e:
        logger.error(f"Refresh token error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function to handle the verify the forgot password email
async def forgot_password_email_verification_post(
    db: AsyncSession, payload: UserForgotPasswordPostRequestModel
):
    try:
        # Check email exists in the database
        email_fetch_query = await db.execute(
            select(Users).where(Users.user_email == payload.user_email)
        )
        email_result = email_fetch_query.scalar_one_or_none()

        # Check if the email exists or not
        if not email_result:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Invalid email address"},
            )

        # Get the otp
        otp = generate_otp()

        # Pass the value of the app name
        app_name = settings.APP_NAME

        user_name = f"{email_result.first_name} {email_result.last_name}"

        # Set the email content
        is_email_sent = await send_email(
            to=payload.user_email,
            subject="Password Reset OTP",
            html_content=build_otp_email(
                otp=otp, user_name=user_name, app_name=app_name
            ),
        )

        # # If the email is not sent then return the error response
        if not is_email_sent:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"success": False, "message": "Failed to send OTP email"},
            )

        # Set the otp in the redis with the expiry time of 5 minutes
        await redis_client.set(f"forgot_password_otp:{payload.user_email}", otp, ex=300)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "OTP Sent Successfully"},
        )

    except Exception as e:
        logger.error(f"Failed to verify the email: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function verify the forgot password otp sent to the user
async def forgot_password_otp_verification_post(
    db: AsyncSession, payload: UserForgotPasswordVerifyOTPPostRequestModel
):
    try:
        # Get the otp from the redis
        stored_otp = await redis_client.get(f"forgot_password_otp:{payload.user_email}")

        # If the otp is not found then return the error response
        if not stored_otp:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "OTP Expired or Invalid"},
            )

        # Check if the otp is valid or not
        if stored_otp != payload.otp:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Invalid OTP"},
            )

        # If the otp is valid then delete it from the redis
        await redis_client.delete(f"forgot_password_otp:{payload.user_email}")

        # Fetch the user details and create the reset token
        email_fetch_query = await db.execute(
            select(Users).where(Users.user_email == payload.user_email)
        )
        user = email_fetch_query.scalar_one()

        # Create the reset token payload
        reset_token_payload = {
            "user_id": str(user.user_id),
            "type": TokenType.PASSWORD_RESET.value,
        }

        # Create the reset token
        reset_token = await create_jwt_token(
            payload=reset_token_payload, token_type=TokenType.PASSWORD_RESET
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "OTP Verified Successfully",
                "reset_token": reset_token,
            },
        )

    except Exception as e:
        logger.error(f"Failed to verify the OTP: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function to handle the reset password after verifying the otp
async def reset_password_post(
    db: AsyncSession, payload: UserResetPasswordPostRequestModel
):
    try:
        # Check if the reset token is valid or not
        # `request` is not available in this context; use the reset_token from the payload
        user_reset_auth = await validate_password_reset_token(payload.reset_token)

        # If the reset token is invalid, return an error response
        if not user_reset_auth:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid or expired reset token"},
            )
        # Fetch the user details and create the reset token
        email_fetch_query = await db.execute(
            select(Users).where(Users.user_id == user_reset_auth.user_id)
        )
        user = email_fetch_query.scalar_one_or_none()

        # If the user is not found, return an error response
        if not user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"success": False, "message": "Invalid email address"},
            )

        # Create the hash of the new password
        hashed_password = hash_password(payload.new_password)

        # Update the user's password in the database
        user.password_hash = hashed_password

        # Commit the changes to the database
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Password Reset Successfully"},
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to reset the password: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Helper function to handle the user logout and delete the session from the database
async def user_logout_post(db: AsyncSession, auth: UserAuth):
    try:
        # Fetch the session from the database
        session_fetch_query = await db.execute(
            select(UserSession).where(
                UserSession.user_session_id == auth.session_id,
                UserSession.user_id == auth.user_id,
                UserSession.is_active,
            )
        )
        session = session_fetch_query.scalar_one_or_none()

        # If the session is not found, return an error response
        if not session:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"success": False, "message": "Invalid User Session"},
            )

        # Mark the session as inactive
        session.is_active = False

        # Commit the changes to the database
        await db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "Logged out successfully"},
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to logout the user: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )
