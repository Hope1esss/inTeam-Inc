from fastapi import APIRouter, Depends, Response

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.db.session import get_session

from app.api.schemas.user import UserCreate, UserLogin

from app.api.services.user_service import create_user, login_user, create_access_token

router = APIRouter()


@router.post("/register", response_model=dict)
async def register(user: UserCreate, session: AsyncSession = Depends(get_session)):
    print(user.username, user.password)
    new_user = await create_user(user_data=user, session=session)
    return {"message": "User created successfully", "user_id": new_user.id}


@router.post("/login", response_model=dict)
async def login(
    response: Response, user: UserLogin, session: AsyncSession = Depends(get_session)
):
    user = await login_user(user_data=user, session=session)
    access_token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, path="/")
    return {'message': 'Login successful'}
