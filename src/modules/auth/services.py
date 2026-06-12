from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.enums import UserRole
from src.modules.auth.models import Users
from src.modules.auth.schemas import (
    UserRegisterPostRequestModel,
)
from src.utils.auth import hash_password


# Function to register the user
async def user_signup_post(db: AsyncSession, payload: UserRegisterPostRequestModel):
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
