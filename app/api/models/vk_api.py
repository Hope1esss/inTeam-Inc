from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.api.db.base import Base


class Hint(Base):
    __tablename__ = "hints"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    sex = Column(Integer)
    bdate = Column(String, nullable=True)
    city = Column(String, nullable=True)
    education = Column(String, nullable=True)
    faculty = Column(String, nullable=True)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    text = Column(String, nullable=True)
    likes = Column(Integer)
    views = Column(Integer)
    img_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
