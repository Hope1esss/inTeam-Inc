from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.api.db.base import Base


class Hint(Base):
    __tablename__ = "hints"
    id = Column(Integer, primary_key=True, index=True)
    sex = Column(Integer)
    bdate = Column(String, nullable=True)
    city = Column(String, nullable=True)
    education = Column(String, nullable=True)


class GiftInfo(Base):
    __tablename__ = "gifts_info"
    id = Column(Integer, primary_key=True, index=True)
    from_id = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    date = Column(Integer)
    gift_id = Column(Integer, nullable=True)
    thumb_256 = Column(String, nullable=True)
    thumb_96 = Column(String, nullable=True)
    thumb_48 = Column(String, nullable=True)


class GiftCount(Base):
    __tablename__ = "gift_counts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True)
    count = Column(Integer)


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    text = Column(String, nullable=True)
    likes = Column(Integer)
    views = Column(Integer)
    img_url = Column(String, nullable=True)
    audio_url = Column(String, nullable=True)
