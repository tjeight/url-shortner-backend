from fastapi import APIRouter

from src.modules.auth.routes import user_auth_router

# User Router
user_router = APIRouter(prefix="/user")


# Include the user_router
user_router.include_router(user_auth_router)
