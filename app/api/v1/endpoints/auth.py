import uuid
from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from app.api.crud.manager import get_user_manager
from app.api.db.base import auth_backend
from app.api.db.init_db import User
from app.api.schemas.user import UserRead, UserCreate

router = APIRouter()

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

register_router = fastapi_users.get_register_router(UserRead, UserCreate)
router.include_router(register_router, tags=["auth"])
login_router = fastapi_users.get_auth_router(auth_backend)
router.include_router(login_router, tags=["auth"])
