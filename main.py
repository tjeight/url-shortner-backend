import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.configs.pg import engine
from src.configs.redis import redis_client
from src.routes.admin import admin_router
from src.routes.user import user_router


async def check_resend_config():

    print("Resend Configured Successfully")


async def check_postgres_connection():
    async with engine.connect() as conn:
        await conn.execute(text("select 1"))
        print("Postgres Connected Successfully")


async def check_redis_connection():
    await redis_client.ping()
    print("Redis Connected Successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_postgres_connection()
    await check_redis_connection()
    await check_resend_config()
    yield


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello from url-shortner-backend!"}


# Include the user router
app.include_router(user_router, prefix="/api/v1")
# Include the admin router
app.include_router(admin_router, prefix="/api/v1")
