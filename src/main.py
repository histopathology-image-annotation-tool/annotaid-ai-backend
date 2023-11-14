from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.api.api_v1.api import api_router
from src.core.config import settings

app = FastAPI()

app.include_router(api_router, prefix=settings.API_V1_STR)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
