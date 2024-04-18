from sqlalchemy.ext.asyncio import create_async_engine

from app.api.core.config import settings
from app.api.db.base import Base

engine = create_async_engine(settings.database_url, echo=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
