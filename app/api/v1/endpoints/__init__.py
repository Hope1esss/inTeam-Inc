from fastapi import APIRouter

from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .data import router as data_router
from .token import router as token_router
from .user import user_router as user_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
router.include_router(data_router, prefix="/data", tags=["data"])
router.include_router(token_router, prefix='/token', tags=['vk_token'])
router.include_router(user_router, prefix='/user', tags=['user'])