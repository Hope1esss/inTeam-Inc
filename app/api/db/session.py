from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.db.init_db import async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
