from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db.session import get_session
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.user_service import (
    create_user,
    login_user,
    create_access_token,
    get_current_user,
)
import asyncio
from app.api.api import Api  # Импортируем ваш парсер

router = APIRouter()


@router.post("/get_id", response_model=dict)
async def get_user_id(user: UserCreate, db: AsyncSession = Depends(get_session)):
    # Ваш код здесь
    pass


@router.post("/user_info/{user_id}", response_model=dict)
async def get_user_info(user_id: str):
    api = Api(user_id)
    await Api.async_db_setup()
    try:
        await api.vk_user_info()
        return {"status": "User info processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wall_posts/{user_id}", response_model=dict)
async def get_wall_posts(user_id: str):
    api = Api(user_id)
    await Api.async_db_setup()
    try:
        await api.vk_wall_posts()
        return {"status": "Wall posts processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
