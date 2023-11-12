from fastapi import APIRouter

from .endpoints import mc, nuclick

api_router = APIRouter()
api_router.include_router(nuclick.router, tags=['NuClick'])
api_router.include_router(mc.router, tags=['Mitosis detection'])
