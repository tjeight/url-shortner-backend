from src.configs.pg import AsyncSessionLocal


# Create the dependency to get the session
async def get_database():
    """Dependency to get the database session"""
    async with AsyncSessionLocal() as session:
        yield session
