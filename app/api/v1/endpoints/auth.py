from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.crud.operations import create_or_update_user
from app.api.db.session import get_session
from app.api.schemas.token import Token
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.user_service import create_user, login_user, create_access_token, get_current_user, get_vk_user_id
from fastapi import Request
from fastapi.responses import JSONResponse
import requests
router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    new_user = await create_user(user_data=user, session=session)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login", response_model=dict)
async def login(
    response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)
):
    user = await login_user(user_data=user, session=session)
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="jwt",
                        value=access_token,
                        path="/",
                        samesite=None)
    return {'message': 'Login successful'}

