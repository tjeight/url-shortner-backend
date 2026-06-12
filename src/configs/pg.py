from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.configs.settings import settings

# Create the async engine
engine = create_async_engine(
    url=settings.database_url,
    pool_size=10,
    max_overflow=20,
)

# Create the session
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)
