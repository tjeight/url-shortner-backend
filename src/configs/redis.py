from redis.asyncio import Redis, ConnectionPool
from src.configs.settings import settings


# Configure the pool
pool = ConnectionPool.from_url(
    url=settings.get_redis_url, decode_responses=True, max_connections=20
)


# Set the redis client
redis_client = Redis(connection_pool=pool)
