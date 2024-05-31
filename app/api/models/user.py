from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.api.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    vk_token = Column(String, nullable=True)
    vk_id = Column(Integer, unique=True, nullable=True)
    expires_in = Column(Integer)
