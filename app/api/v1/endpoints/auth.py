from fastapi import APIRouter, HTTPException
from alchemy_authentication_system.auth_system import AuthenticationSystem
from alchemy_authentication_system.errors import (
    UserAlreadyExistsError,
    UserNotFoundError,
    WrongPasswordError,
)


router = APIRouter()


@router.post("/auth/register")
async def register(login: str, password: str):
    try:
        AuthenticationSystem().registration(login, password)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Пользователь успешно зарегистрирован."}


@router.post("/auth/login")
async def login(login: str, password: str):
    try:
        AuthenticationSystem().login(login, password)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WrongPasswordError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"message": "Успешный вход."}


@router.post("/auth/logout")
async def logout():
    AuthenticationSystem().logout()
    return {"message": "Вы успешно вышли из системы."}
