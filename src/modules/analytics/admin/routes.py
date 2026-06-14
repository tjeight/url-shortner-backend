from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.analytics.admin.services import admin_analytics_get
from src.dependencies.pg import get_database
from src.modules.auth.admin.schemas import AdminAuth
from src.utils.auth import validate_admin_auth

# Configure the admin analytics routes
admin_analytics_router = APIRouter(prefix="/analytics")


@admin_analytics_router.get("/urls")
async def admin_analytics_get_call(
    db: AsyncSession = Depends(get_database),
    _auth: AdminAuth = Depends(validate_admin_auth),
):
    return await admin_analytics_get(db=db)
