from fastapi import APIRouter

from src.modules.auth.user.routes import user_auth_router
from src.modules.urls.user.routes import user_url_router
from src.modules.analytics.users.routes import user_analytics_router

# User Router
user_router = APIRouter(prefix="/user")


# Include the user_router
user_router.include_router(user_auth_router)

# Include the user url router
user_router.include_router(user_url_router)

# Include the user analytics router
user_router.include_router(user_analytics_router)
