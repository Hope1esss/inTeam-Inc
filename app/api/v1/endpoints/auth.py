from datetime import datetime

from fastapi import APIRouter, Depends, Response, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.services.security import hash_password
from app.api.crud.operations import create_or_update_user
from app.api.db.session import get_session
from app.api.schemas.token import Token
from app.api.schemas.user import UserCreate, UserLogin, User, RegisterVk, LoginVk
import app.api.models.user as user_m
from app.api.services.user_service import (
    create_user,
    login_user,
    create_access_token,
    get_current_user,
    get_vk_user_info,
)
from fastapi import Request
from fastapi.responses import JSONResponse
import requests

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    new_user = await create_user(user_data=user, session=session)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login", response_model=dict)
async def login(
    response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)
):
    user = await login_user(user_data=user, session=session)
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="jwt", value=access_token, path="/", samesite=None)
    return {"message": "Login successful"}


@router.post("/register_vk", response_model=dict    )
async def register_user(request: RegisterVk, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(user_m.User).filter(user_m.User.vk_id == request.vk_id)
    )
    user = result.scalars().first()

    if user:
        vk_user_info = await get_vk_user_info(request.access_token)
        username = f"{vk_user_info['first_name']} {vk_user_info['last_name']}"
        avatar_url = vk_user_info.get("photo_200", "")
        print(vk_user_info)
        user.vk_token = request.access_token
        user.expires_in = request.expires_in
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)

        return {
            "message": "User logged in successfully",
            "user_id": user.id,
            "username": username,
            "avatar_url": avatar_url,
            "expires_in": request.expires_in,
            "access_token": request.access_token,
        }

    vk_user_info = await get_vk_user_info(request.access_token)
    username = f"{vk_user_info['first_name']} {vk_user_info['last_name']}"
    avatar_url = vk_user_info.get("photo_200", "")
    new_user = user_m.User(
        vk_id=request.vk_id,
        vk_token=request.access_token,
        username=username,
        hashed_password=hash_password(request.password),
        expires_in=request.expires_in,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "username": username,
        "avatar_url": avatar_url,
        "expires_in": request.expires_in,
        "access_token": request.access_token,
    }
