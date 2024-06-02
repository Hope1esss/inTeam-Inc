from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db.session import get_session
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.api import Api
from app.api.services.gigachat import gigachat_short_content
from app.api.services.user_service import (
    create_user,
    login_user,
    create_access_token,
    get_current_user,
)
from app.api.core.config import settings

router = APIRouter()


@router.post("/get_id", response_model=dict)
async def get_user_id(user: UserCreate, db: AsyncSession = Depends(get_session)):
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


@router.post("/gifts_info/{user_id}")
async def get_gifts_info(
    user_id: int, access_token: str, db: AsyncSession = Depends(get_session)
):
    vk_service = Api(user_id=user_id, token=access_token)
    try:
        gifts_info = await vk_service.vk_gifts_info(db)
        return {"response": gifts_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gifts_count/{user_id}")
async def get_gifts_count(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    vk_service = Api(user_id=user_id, token=access_token)
    try:
        gifts_count = await vk_service.vk_gifts_count(db)
        return {"gift_count": gifts_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wall_posts/{user_id}")
async def get_wall_posts(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id=user_id, token=access_token)
    try:
        data = await api.vk_wall_posts(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/{user_id}")
async def analyze_user(user_id: str, db: AsyncSession = Depends(get_session)):
    try:
        data = await analyze_with_gigachat(db, user_id)
        return {"response": data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze_with_gigachat/{user_id}")
async def gigachat_short_content(user_id: str, db: AsyncSession = Depends(get_session)):
    try:
        data = await gigachat_short_content(db, user_id)
        return {"response": data}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
