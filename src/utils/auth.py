import hashlib
import logging

import jwt
from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.pg import get_database
from src.modules.auth.user.models import UserSession
from src.modules.auth.user.schemas import UserAuth, UserResetAuth
from src.configs.settings import settings
from src.modules.auth.user.enums import TokenType, UserRole

logger = logging.getLogger(__name__)

# Set the crypto context
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper function hash the password
def hash_password(password: str) -> str:
    return password_context.hash(password)


# Helper Function to verify the password
def verify_hashed_password(hashed_password, password) -> bool:
    return password_context.verify(
        secret=password,
        hash=hashed_password,
    )


# Helper Function to create the access token and refresh token
async def create_jwt_token(payload: dict, token_type: TokenType) -> str:
    # Copy the dic
    data = payload.copy()

    # Set the expiry time based on the token type
    if token_type == TokenType.ACCESS_TOKEN:
        expiry_time = settings.get_access_token_expiry_minutes
    elif token_type == TokenType.REFRESH_TOKEN:
        expiry_time = settings.get_refresh_token_expiry_days
    elif token_type == TokenType.PASSWORD_RESET:
        expiry_time = settings.get_access_token_expiry_minutes

    # Update the expiry time
    data["exp"] = expiry_time

    # Encode the token
    token = jwt.encode(
        algorithm=settings.JWT_ALGORITHM, payload=data, key=settings.JWT_SECRET_KEY
    )

    return token


# Helper Function to get the client info
def get_client_info(request: Request) -> tuple[str, str]:
    # Safely get client host in case request.client is None
    client_host = getattr(getattr(request, "client", None), "host", None)
    ip_address = (
        request.headers.get("X-Forwarded-For", client_host or "Unknown")
        .split(",")[0]
        .strip()
    )

    device_info = request.headers.get(
        "User-Agent",
        "Unknown Device",
    )

    return ip_address, device_info


# Hash the refresh token using SHA-256 to store in the database
def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# Check the user has the access token
async def validate_user_auth(
    request: Request, db: AsyncSession = Depends(get_database)
) -> UserAuth:
    try:
        # Get access token from cookie
        access_token = request.cookies.get("access_token")

        # Proper HTTP exception
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing"
            )

        # Decode token
        payload = jwt.decode(
            jwt=access_token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Verify token type
        if payload.get("type") != TokenType.ACCESS_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        # Extract payload fields
        user_id = payload.get("user_id")
        role = payload.get("role")
        session_id = payload.get("session_id")
        token_type = payload.get("type")

        # Validate all fields present
        if not all([user_id, role, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        if token_type != TokenType.ACCESS_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token Type"
            )
        # Validate session exists and is active in DB
        session = await db.scalar(
            select(UserSession).where(
                UserSession.user_session_id == session_id, UserSession.is_active
            )
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or logged out",
            )

        return UserAuth(
            user_id=str(user_id),
            role=str(role),
            session_id=str(session_id),
        )

    except HTTPException:
        raise  #  Let HTTPExceptions pass through untouched

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Auth validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


async def validate_refresh_token(
    request: Request, db: AsyncSession = Depends(get_database)
) -> UserAuth:
    try:
        # Fetch the refresh token from the request
        refresh_token_jwt = request.cookies.get("refresh_token")

        # Check if the refresh token is valid or not
        if not refresh_token_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Refresh Token"
            )

        # Decode the jwt
        refresh_token = jwt.decode(
            jwt=refresh_token_jwt,
            algorithms=[settings.JWT_ALGORITHM],
            key=settings.JWT_SECRET_KEY,
        )

        # Check the type of the token
        user_id = refresh_token["user_id"]
        role = refresh_token["role"]
        session_id = refresh_token["session_id"]
        token_type = refresh_token["type"]

        # Validate all fields present
        if not all([user_id, role, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        if token_type != TokenType.REFRESH_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token Type"
            )

        # Check the session id
        session = await db.scalar(
            select(UserSession).where(
                UserSession.user_session_id == session_id,
                UserSession.user_id == user_id,
                UserSession.is_active,
            )
        )

        # Check if the session is active
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User Session"
            )

        return UserAuth(session_id=session_id, role=role, user_id=user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided Expired Refresh Token",
        )

    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Auth validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


async def validate_password_reset_token(password_reset_token_jwt: str) -> UserResetAuth:
    try:
        # Check if the password reset token is valid or not
        if not password_reset_token_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Password Reset Token",
            )

        # Decode the jwt
        password_reset_token = jwt.decode(
            jwt=password_reset_token_jwt,
            algorithms=[settings.JWT_ALGORITHM],
            key=settings.JWT_SECRET_KEY,
        )

        user_id = password_reset_token["user_id"]
        token_type = password_reset_token["type"]

        if not all([user_id, token_type]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        if token_type != TokenType.PASSWORD_RESET.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token Type"
            )

        return UserResetAuth(user_id=password_reset_token["user_id"])

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided Expired Password Reset Token",
        )

    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Password Reset Token",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Auth validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


# Check the admin has the access token
async def validate_admin_auth(
    request: Request, db: AsyncSession = Depends(get_database)
) -> UserAuth:
    try:
        # Get access token from cookie
        access_token = request.cookies.get("access_token")

        # Check if the access token is present
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token missing"
            )

        # Decode token
        payload = jwt.decode(
            jwt=access_token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # Extract payload fields
        user_id = payload.get("user_id")
        role = payload.get("role")
        session_id = payload.get("session_id")
        token_type = payload.get("type")

        # Validate all fields present
        if not all([user_id, role, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Verify token type is access token
        if token_type != TokenType.ACCESS_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        # Verify the role is admin
        if role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        # Validate session exists and is active in DB
        session = await db.scalar(
            select(UserSession).where(
                UserSession.user_session_id == session_id, UserSession.is_active
            )
        )

        # Check if the session is active
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or logged out",
            )

        return UserAuth(
            user_id=str(user_id),
            role=str(role),
            session_id=str(session_id),
        )

    except HTTPException:
        raise

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Admin auth validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


# Check the admin has the refresh token
async def validate_admin_refresh_token(
    request: Request, db: AsyncSession = Depends(get_database)
) -> UserAuth:
    try:
        # Fetch the refresh token from the request
        refresh_token_jwt = request.cookies.get("refresh_token")

        # Check if the refresh token is valid or not
        if not refresh_token_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Refresh Token"
            )

        # Decode the jwt
        refresh_token = jwt.decode(
            jwt=refresh_token_jwt,
            algorithms=[settings.JWT_ALGORITHM],
            key=settings.JWT_SECRET_KEY,
        )

        # Extract the token fields
        user_id = refresh_token["user_id"]
        role = refresh_token["role"]
        session_id = refresh_token["session_id"]
        token_type = refresh_token["type"]

        # Validate all fields present
        if not all([user_id, role, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
            )

        # Verify token type is refresh token
        if token_type != TokenType.REFRESH_TOKEN.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token Type"
            )

        # Verify the role is admin
        if role != UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )

        # Check the session exists and is active
        session = await db.scalar(
            select(UserSession).where(
                UserSession.user_session_id == session_id,
                UserSession.user_id == user_id,
                UserSession.is_active,
            )
        )

        # Check if the session is active
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Admin Session"
            )

        return UserAuth(session_id=session_id, role=role, user_id=user_id)

    except HTTPException:
        raise

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Provided Expired Refresh Token",
        )

    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        logger.error(f"Admin refresh token validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
