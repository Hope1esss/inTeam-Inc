from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.api.db.init_db import engine

async_sesion = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
