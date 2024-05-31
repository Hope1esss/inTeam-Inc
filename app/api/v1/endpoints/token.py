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