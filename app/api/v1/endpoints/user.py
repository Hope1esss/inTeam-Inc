from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db.session import get_session
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.api import Api
from app.api.services.user_service import (
    create_user,
    login_user,
    create_access_token,
    get_current_user,
)
import asyncio


router = APIRouter()


@router.post("/get_id", response_model=dict)
async def get_user_id(user: UserCreate, db: AsyncSession = Depends(get_session)):
    # Ваш код здесь
    pass


@router.post("/user_info/{user_id}", response_model=dict)
async def get_user_info(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id, access_token)
    try:
        data = await api.vk_user_info(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wall_posts/{user_id}")
async def get_wall_posts(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id, access_token)
    try:
        data = await api.vk_wall_posts(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
