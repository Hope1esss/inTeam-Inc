from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=50)


class UserLogin(UserBase):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    vk_token: str = None

    class Config:
        from_attributes = True


class LoginVk(BaseModel):
    access_token: str
    vk_id: int
    expires_in: int


class RegisterVk(LoginVk):
    password: str
