import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.urls.user.models import LinkUrl
from src.modules.urls.user.payloads import get_user_url_payload
from src.modules.auth.user.schemas import UserAuth
from src.utils.cache import get_cache, set_cache
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate


# Helper function to generate the random string for the short URL
def generate_short_code(length: int = 7):
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


# Helper Function to get the cache key for the user
def get_cache_key(page: int, size: int, user_id: str) -> str:
    return f"urls:{user_id}:{page}:{size}"


# Helper Function to cache the data according to the user
async def cache_user_urls(
    db: AsyncSession, auth: UserAuth, page: int = 1, size: int = 10
) -> dict | None:
    # Get the cache key
    cache_key = get_cache_key(user_id=str(auth.user_id), page=page, size=size)

    # Fetch from cache first
    cached_data = await get_cache(key=cache_key)

    # Return cached data if present
    if cached_data:
        return cached_data if isinstance(cached_data, dict) else None

    # Set the params
    params = Params(page=page, size=size)

    # Fetch from the database with pagination
    user_urls_fetch_query = (
        select(LinkUrl)
        .where(
            LinkUrl.user_id == auth.user_id,
            LinkUrl.is_active,
        )
        .order_by(LinkUrl.created_at.desc())
    )

    # Pass to the paginate
    user_url_paginated_result = await paginate(
        conn=db, query=user_urls_fetch_query, params=params
    )

    user_urls = user_url_paginated_result.items

    # Return None if no URLs found
    if not user_urls:
        return None

    # Serialize the urls using the payload function
    user_urls_to_cache = [get_user_url_payload(link_url=url) for url in user_urls]

    # Build the cache data with pagination metadata
    cache_data = {
        "pagination": {
            "page": page,
            "size": size,
            "total": user_url_paginated_result.total,
        },
        "user_urls": user_urls_to_cache,
    }

    # Set the cache with 3 minute TTL
    await set_cache(key=cache_key, data=cache_data, ttl=180)

    # Return cache_data not user_urls_to_cache
    return cache_data


# Function to get the cache key for the url
def get_single_url_cache_key(short_code: str) -> str:
    return f"url:{short_code}"


# Function to handle the get url from cache
async def cache_redirect_url(
    db: AsyncSession,
    short_code: str,
) -> dict | None:
    # Get the cache key
    cache_key = get_single_url_cache_key(short_code=short_code)

    # Get the cache
    cached_data = await get_cache(
        key=cache_key,
    )

    # Check if the cache exits
    if cached_data:
        return cached_data if isinstance(cached_data, dict) else None

    # Fetch the short url
    url_fetch_query = select(LinkUrl).where(
        LinkUrl.short_code == short_code,
        LinkUrl.is_active,
    )

    url_result = await db.execute(url_fetch_query)

    url = url_result.scalar_one_or_none()

    print("URL fetched from database for short code:", short_code, "URL:", url)
    # If url not found return None
    if not url:
        return None

    # Create the cache data
    cache_data = {
        "long_url": url.long_url,
        "expires_at": url.expires_at.isoformat(),
    }

    # Set the cache with 3 minute TTL
    await set_cache(key=cache_key, data=cache_data, ttl=180)

    return cache_data
