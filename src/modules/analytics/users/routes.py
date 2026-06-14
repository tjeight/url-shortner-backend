from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.pg import get_database
from src.modules.analytics.users.services import user_url_analytics_get
from src.modules.auth.user.schemas import UserAuth
from src.utils.auth import validate_user_auth

# Configure the analytics router
user_analytics_router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


# Route to get the analytics for the user urls
@user_analytics_router.get("/urls", summary="Get analytics for user URLs")
async def get_user_url_analytics(
    auth: UserAuth = Depends(validate_user_auth),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: AsyncSession = Depends(get_database),
):
    return await user_url_analytics_get(db=db, auth=auth, page=page, size=size)
