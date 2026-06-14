from fastapi import APIRouter
from src.modules.analytics.admin.routes import admin_analytics_router
from src.modules.auth.admin.routes import admin_auth_router

admin_router = APIRouter(prefix="/admin")


# Include the admin auth router
admin_router.include_router(admin_auth_router)

# Include the admin
admin_router.include_router(admin_analytics_router)
