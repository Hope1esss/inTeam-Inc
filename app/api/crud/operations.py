from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.db.session import get_session
from app.api.models.user import User
from app.api.schemas.token import Token


async def get_user_by_vk_user_id(db: AsyncSession, vk_user_id: int):
    result = await db.execute(select(User).filter(User.vk_user_id == vk_user_id))
    return result.scalars().first()


async def create_or_update_user(
    db: AsyncSession, vk_user_id: int, username: str, access_token: str
):
    user = await get_user_by_vk_user_id(db, vk_user_id)
    if user:
        user.vk_token = access_token
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
    else:
        user = User(
            vk_user_id=vk_user_id,
            username=username,
            vk_token=access_token,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
