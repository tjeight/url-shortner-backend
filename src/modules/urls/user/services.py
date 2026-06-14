import logging
from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.settings import settings
from src.modules.auth.user.schemas import UserAuth
from src.modules.urls.user.helpers import (
    cache_redirect_url,
    cache_user_urls,
    generate_short_code,
)
from src.modules.urls.user.models import LinkUrl
from src.modules.urls.user.schemas import (
    UserURLDeleteRequestModel,
    UserURLPostRequestModel,
    UserURLRefreshRequestModel,
)
from src.utils.cache import delete_cache, delete_cache_by_pattern

logger = logging.getLogger(__name__)


# User Function to store the short url
async def url_short_post(
    db: AsyncSession, payload: UserURLPostRequestModel, auth: UserAuth
):
    try:
        # Check if the long URL already exists for this user — return existing short code
        url_fetch_query = await db.execute(
            select(LinkUrl).where(
                LinkUrl.long_url == str(payload.long_url),
                LinkUrl.user_id == auth.user_id,
            )
        )
        url = url_fetch_query.scalar_one_or_none()

        if url:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Short URL already exists",
                    "short_url": f"{settings.BASE_URL}/{url.short_code}",
                },
            )

        # Calculate the expiry date for the short URL (30 days from now)
        expires_at = datetime.now(UTC) + timedelta(days=30)

        # Retry loop to handle short code collisions
        for _ in range(5):
            short_code = generate_short_code()

            try:
                # Insert into the database
                new_url = LinkUrl(
                    user_id=auth.user_id,
                    long_url=str(payload.long_url),
                    short_code=short_code,
                    expires_at=expires_at,
                )

                db.add(new_url)

                # Commit to trigger unique constraint check
                await db.commit()

                # On URL create or delete — invalidate all pages for that user
                await delete_cache_by_pattern(f"urls:{auth.user_id}:*")

                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "success": True,
                        "message": "Short URL created successfully",
                        "short_url": f"{settings.BASE_URL}/{short_code}",
                    },
                )

            except IntegrityError:
                # Short code collision — rollback and retry with new code
                await db.rollback()
                continue

        # Delete the cache

        # All 5 retries failed
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Failed to generate unique short code",
            },
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"URL shortening error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# User Function to get all the long urls for the user and expiry time
async def url_short_get(
    db: AsyncSession, auth: UserAuth, page: int = 1, size: int = 10
):
    try:
        # Fetch all the urls for the user
        user_urls = await cache_user_urls(db=db, auth=auth, page=page, size=size)

        # Check if the user urls are present or not
        if not user_urls:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "success": True,
                    "message": "Urls Retrieved SuccessFully",
                    "pagination": {},
                    "user_urls": [],
                },
            )

        # Return the response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Urls Retrieved SuccessFully",
                "pagination": user_urls["pagination"],
                "user_urls": user_urls["user_urls"],
            },
        )

    except Exception as e:
        logger.error(f"URL shortening error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function to handle the user url redirect get
async def url_redirect_get(db: AsyncSession, short_code: str):
    try:
        print("Redirect URL called with short code:", short_code)
        # Fetch the url from the cache
        user_url_result = await cache_redirect_url(db=db, short_code=short_code)

        current_time = datetime.now(UTC)
        # Check if the user_url_exists
        if not user_url_result:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": "Redirect URL not found",
                    "redirect_url": "",
                },
            )

        # Check the expiry
        if datetime.fromisoformat(user_url_result["expires_at"]) < current_time:
            await delete_cache(f"url:{short_code}")
            return JSONResponse(
                status_code=status.HTTP_410_GONE,
                content={
                    "success": True,
                    "message": "URL Expired",
                    "redirect_url": "",
                },
            )

        # Return the response
        return RedirectResponse(
            url=user_url_result["long_url"],
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    except Exception as e:
        logger.error(f"URL shortening error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


async def user_url_delete(
    db: AsyncSession, payload: UserURLDeleteRequestModel, auth: UserAuth
):
    try:
        user_url_fetch_query = await db.execute(
            select(LinkUrl).where(
                LinkUrl.user_id == auth.user_id,
                LinkUrl.link_url_id == payload.link_url_id,
            )
        )

        user_url = user_url_fetch_query.scalar_one_or_none()

        if not user_url:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": "URL not found",
                },
            )

        user_delete_short_code = user_url.short_code

        # Delete the url
        await db.delete(user_url)

        # Commit the changes to the database
        await db.commit()

        # Delete the cache
        await delete_cache_by_pattern(f"urls:{auth.user_id}:*")
        await delete_cache(f"url:{user_delete_short_code}")

        # Return the response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "URL Delete SuccessFully"},
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error delete the url:{e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )


# Function to handle the user url refresh
async def user_url_refresh(
    db: AsyncSession, auth: UserAuth, payload: UserURLRefreshRequestModel
):
    try:
        user_url_fetch_query = await db.execute(
            select(LinkUrl).where(
                LinkUrl.user_id == auth.user_id,
                LinkUrl.link_url_id == payload.link_url_id,
            )
        )

        user_url = user_url_fetch_query.scalar_one_or_none()

        if not user_url:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "success": False,
                    "message": "URL not found",
                },
            )

        # Update the expiry date for the short URL (30 days from now)
        user_url.expires_at = datetime.now(UTC) + timedelta(days=30)

        # Commit the changes to the database
        await db.commit()

        # Delete the cache
        await delete_cache_by_pattern(f"urls:{auth.user_id}:*")
        await delete_cache(f"url:{user_url.short_code}")

        # Return the response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "message": "URL Refreshed SuccessFully"},
        )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error refresh the url:{e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": "Internal Server Error"},
        )
