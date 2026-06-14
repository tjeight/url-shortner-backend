import json
import logging

from src.configs.redis import redis_client

logger = logging.getLogger(__name__)


# Helper Function to set the cache
async def set_cache(key: str, data: dict | list, ttl: int = 300) -> bool:
    try:
        await redis_client.set(key, json.dumps(data), ex=ttl)
        return True
    except Exception as e:
        logger.error(f"Redis set error: {e}", exc_info=True)
        return False


# Helper Function to get the cache
async def get_cache(key: str) -> dict | list | None:
    try:
        value = await redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"Redis get error: {e}", exc_info=True)
        return None


# Helper Function to delete the cache
async def delete_cache(key: str) -> bool:
    try:
        await redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Redis delete error: {e}", exc_info=True)
        return False


# Helper Function to delete the cache by pattern
async def delete_cache_by_pattern(pattern: str) -> bool:
    try:
        # SCAN to find all keys matching the pattern
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)

        # Delete all found keys
        if keys:
            await redis_client.delete(*keys)

        return True
    except Exception as e:
        logger.error(f"Redis delete by pattern error: {e}", exc_info=True)
        return False
