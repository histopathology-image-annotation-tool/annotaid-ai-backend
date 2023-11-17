from fastapi import APIRouter

from .endpoints import mc, np, nuclick

api_router = APIRouter()
api_router.include_router(nuclick.router, tags=['NuClick'])
api_router.include_router(mc.router, tags=['Mitosis detection'])
api_router.include_router(np.router, tags=['Nuclear pleomorphism'])
