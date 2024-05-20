from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db.session import get_session
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.user_service import create_user, login_user, create_access_token, get_current_user

router = APIRouter()


@router.post("/get_id", response_model=dict)