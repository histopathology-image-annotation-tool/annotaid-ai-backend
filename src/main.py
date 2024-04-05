from fastapi import FastAPI

from src.api.api_v1.api import api_router
from src.core.config import settings

from .middlewares import middleware

app = FastAPI(middleware=middleware)

app.include_router(api_router, prefix=settings.API_V1_STR)
