from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from src.configs.pg import engine
from src.routes.user import user_router
import logging


async def check_postgres_connection():
    async with engine.connect() as conn:
        await conn.execute(text("select 1"))
        print("Postgres Connected Successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_postgres_connection()
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
