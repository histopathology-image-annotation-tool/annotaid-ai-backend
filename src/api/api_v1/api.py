from fastapi import APIRouter

from .endpoints import active_learning, mc, np, nuclick, sam

api_router = APIRouter()
api_router.include_router(nuclick.router, tags=['NuClick'])
api_router.include_router(mc.router, tags=['Mitosis detection'])
api_router.include_router(np.router, tags=['Nuclear pleomorphism'])
api_router.include_router(sam.router, tags=['SAM (Segment Anything Model)'])
api_router.include_router(active_learning.router, tags=['Active learning'])
