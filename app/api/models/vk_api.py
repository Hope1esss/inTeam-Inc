from sqlalchemy import Column, Integer, String,  UniqueConstraint, Boolean, DateTime

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
    description  = Column(String, nullable=True)


class GiftInfo(Base):
    __tablename__ = "gifts_info"
    user_id = Column(Integer, primary_key=True, nullable=False)
    from_id = Column(Integer, primary_key=True, nullable=False)
    from_id_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'from_id', name='unique_user_from'),
    )


class GiftCount(Base):
    __tablename__ = "gift_count"
    user_id = Column(String, primary_key=True, unique=True)
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
