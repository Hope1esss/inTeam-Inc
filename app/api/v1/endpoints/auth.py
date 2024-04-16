from fastapi import APIRouter, HTTPException
import authentication_system

router = APIRouter()


@router.post("/auth/register")
async def register(login: str, password: str):
    auth_system = authentication_system.AuthenticationSystem()
    try:
        auth_system.adding_user(login, password)
    except authentication_system.errors.UserAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "User has been registered."}


@router.post("/auth/login")
async def login(login: str, password: str):
    auth_system = authentication_system.AuthenticationSystem()
    if auth_system.login(login, password):
        return {"message": "User has been logged in."}
    return {"message": "Invalid credentials."}


@router.post("/auth/logout")
async def logout():
    auth_system = authentication_system.AuthenticationSystem()
    auth_system.logout()
    return {"message": "User has been logged out."}
