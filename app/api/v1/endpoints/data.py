from fastapi import APIRouter, Depends
from app.api.db.init_db import User
from app.api.services.user_service import get_current_user

router = APIRouter()


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
