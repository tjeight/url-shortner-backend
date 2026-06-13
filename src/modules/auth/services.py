import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.settings import settings
from src.modules.auth.enums import TokenType, UserRole
from src.modules.auth.models import Users, UserSession
from time import perf_counter

# Set the logger

from src.modules.auth.schemas import (
    UserLoginPostRequestModel,
    UserRegisterPostRequestModel,
)
from src.utils.auth import (
    create_jwt_token,
    get_client_info,
    hash_password,
    hash_refresh_token,
    verify_hashed_password,
)

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
        token_payload = {
            "user_id": str(user.user_id),
            "role": user.role,
            "session_id": str(new_session.user_session_id),
        }

        # Create tokens
        access_token = await create_jwt_token(token_payload, TokenType.ACCESS_TOKEN)
        refresh_token = await create_jwt_token(token_payload, TokenType.REFRESH_TOKEN)
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
