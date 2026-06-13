from fastapi import APIRouter
from src.modules.auth.admin.routes import admin_auth_router

admin_router = APIRouter(prefix="/admin")


# Include the admin auth router
admin_router.include_router(admin_auth_router)
