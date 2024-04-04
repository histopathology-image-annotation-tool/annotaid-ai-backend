from fastapi import FastAPI

from src.api.api_v1.api import api_router
from src.core.config import settings
from src.core.database import engine

from . import db_models
from .middlewares import middleware


async def on_startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(db_models.Base.metadata.create_all)


app = FastAPI(middleware=middleware, on_startup=[on_startup])

app.include_router(api_router, prefix=settings.API_V1_STR)
