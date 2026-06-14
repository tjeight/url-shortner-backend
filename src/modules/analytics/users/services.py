import logging

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.user.schemas import UserAuth
from src.modules.analytics.users.models import URLClick
from src.modules.analytics.users.payloads import get_user_click_payload
from src.modules.urls.user.models import LinkUrl

logger = logging.getLogger(__name__)


# User Function to handle the user url redirect get
async def user_url_analytics_get(
    db: AsyncSession,
    auth: UserAuth,
    page: int = 1,
    size: int = 10,
):
    try:
        # Total URLs created by the user
        total_urls_query = await db.execute(
            select(func.count(LinkUrl.link_url_id)).where(
                LinkUrl.user_id == auth.user_id
            )
        )

        total_urls = total_urls_query.scalar() or 0

        # Total clicks across all URLs
        total_clicks_query = await db.execute(
            select(func.count(URLClick.url_click_id))
            .join(
                LinkUrl,
                URLClick.link_url_id == LinkUrl.link_url_id,
            )
            .where(LinkUrl.user_id == auth.user_id)
        )

        total_clicks = total_clicks_query.scalar() or 0

        # Unique visitors
        unique_visitors_query = await db.execute(
            select(func.count(func.distinct(URLClick.ip_address)))
            .join(
                LinkUrl,
                URLClick.link_url_id == LinkUrl.link_url_id,
            )
            .where(LinkUrl.user_id == auth.user_id)
        )

        unique_visitors = unique_visitors_query.scalar() or 0

        # Last click timestamp
        last_click_query = await db.execute(
            select(func.max(URLClick.clicked_at))
            .join(
                LinkUrl,
                URLClick.link_url_id == LinkUrl.link_url_id,
            )
            .where(LinkUrl.user_id == auth.user_id)
        )

        last_clicked_at = last_click_query.scalar()

        # Detailed click history
        clicks_query = (
            select(URLClick)
            .join(
                LinkUrl,
                URLClick.link_url_id == LinkUrl.link_url_id,
            )
            .where(LinkUrl.user_id == auth.user_id)
            .order_by(URLClick.clicked_at.desc())
        )

        paginated_result = await paginate(
            conn=db,
            query=clicks_query,
            params=Params(page=page, size=size),
        )

        clicks_data = [
            get_user_click_payload(click=click) for click in paginated_result.items
        ]

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Analytics retrieved successfully",
                "pagination": {
                    "page": page,
                    "size": size,
                    "total": paginated_result.total,
                },
                "analytics": {
                    "total_urls": total_urls,
                    "total_clicks": total_clicks,
                    "unique_visitors": unique_visitors,
                    "last_clicked_at": (
                        last_clicked_at.isoformat() if last_clicked_at else ""
                    ),
                    "clicks": clicks_data,
                },
            },
        )

    except Exception as e:
        await db.rollback()

        logger.error(
            f"Failed to get analytics: {e}",
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal Server Error",
            },
        )
