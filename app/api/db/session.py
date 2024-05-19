from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.api.db.init_db import engine

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session
