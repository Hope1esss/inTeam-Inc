from sqlalchemy.ext.asyncio import create_async_engine

from app.api.core.config import settings
from app.api.db.base import Base
from app.api.models.user import User  # noqa # pylint: disable=unused-import
from app.api.models.vk_api import Hint, Post

engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
