import httpx
from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.crud.operations import create_or_update_user
from app.api.db.session import get_session
from app.api.schemas.token import Token, CodeRequest
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.user_service import create_user, login_user, create_access_token, get_current_user, get_vk_user_id
from fastapi import Request
from fastapi.responses import JSONResponse
from app.api.core.config import settings
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


@router.get("/proxy_vk_access_token")
async def proxy_vk_access_token(code: str):
    client_id = '51899044'  # Замените на ваш client_id
    client_secret = 'uLb2f2a4zsBkpyOjSQsV'  # Замените на ваш client_secret
    redirect_uri = 'https://4894-195-123-219-158.ngrok-free.app/callback.html'  # URL, на который был передан code

    token_url = f"https://oauth.vk.com/access_token?client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}"

    response = requests.get(token_url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error_description"])

    access_token = data["access_token"]
    user_id = data["user_id"]

    # Здесь вы можете создать или обновить пользователя в базе данных
    # user = await create_or_update_user(access_token)

    return JSONResponse(content={"access_token": access_token, "user_id": user_id})

@router.post("/vk")
async def auth_vk(data: dict, session: AsyncSession = Depends(get_session)):
    access_token = data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is required")

    user_info_url = f"https://api.vk.com/method/users.get?access_token={access_token}&v=5.131"
    response = requests.get(user_info_url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    user_data = response.json()
    if "error" in user_data:
        raise HTTPException(status_code=400, detail=user_data["error"]["error_msg"])

    user_info = user_data["response"][0]
    username = user_info["first_name"] + " " + user_info["last_name"]

    print(user_data, access_token)
    user = await create_or_update_user(db=session, vk_user_id=user_info["id"], username=username, access_token=access_token)

    return JSONResponse(content={"message": "User authenticated", "username": username})


@router.get("/check-token", response_model=dict)
async def check_token(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "user_id": current_user.id}


@router.post("/get_access_token")
async def get_access_token(request: CodeRequest):
    code = request.code
    url = "https://oauth.vk.com/access_token"
    params = {
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'redirect_uri': settings.REDIRECT_URI,
        'code': code
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response_data = response.json()

    if 'access_token' in response_data:
        return {
            'access_token': response_data['access_token'],
            'expires_in': response_data['expires_in'],
            'user_id': response_data['user_id']
        }
    else:
        return {
            'error': response_data.get('error'),
            'error_description': response_data.get('error_description')
        }