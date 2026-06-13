import jwt
from fastapi import Request
from passlib.context import CryptContext

from src.configs.settings import settings
from src.modules.auth.enums import TokenType
import hashlib

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

    # Check the token type and get the expiry time
    expiry_time = (
        settings.get_access_token_expiry_minutes
        if token_type == TokenType.ACCESS_TOKEN
        else settings.get_refresh_token_expiry_days
    )

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
