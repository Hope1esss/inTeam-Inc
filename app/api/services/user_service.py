from datetime import timedelta, datetime

import httpx
from jose import jwt, JWTError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from fastapi import HTTPException, Depends

from app.api.core.config import settings
from app.api.db.session import get_session
from app.api.models.user import User
from app.api.schemas.user import UserCreate, UserLogin
from app.api.services.security import hash_password, verify_password
import requests


async def create_user(user_data: UserCreate, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).filter(User.username == user_data.username)
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def login_user(user_data: UserLogin, session: AsyncSession) -> User:
    result = await session.execute(
        select(User).filter(User.username == user_data.username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return user


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        result = await session.execute(select(User).filter(User.id == int(user_id)))
        user: User = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="JWT fake") from exc


async def get_vk_user_info(access_token: str):
    url = "https://api.vk.com/method/users.get"
    params = {"access_token": access_token, "v": "5.131", "fields": "photo_200"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response_data = response.json()
        if "error" in response_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error retrieving user info from VK",
            )
        return response_data["response"][0]
