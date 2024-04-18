from datetime import timedelta, datetime
from jose import jwt, JWTError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.core.config import settings
from app.api.db.session import get_session
from app.api.models.user import User
from app.api.schemas.user import UserCreate, UserLogin
from app.api.services.security import hash_password
from fastapi import HTTPException, Depends
from app.api.services.security import verify_password


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
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    request: Request, session: AsyncSession = Depends(get_session)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        result = await session.execute(select(User).filter(User.id == user_id))
        user: User = result.scalars().first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")
