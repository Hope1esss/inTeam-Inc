from fastapi import APIRouter

router = APIRouter()


@router.post("/auth/register")
async def register():
    pass


@router.post("/auth/login")
async def login():
    pass


@router.post("/auth/logout")
async def logout():
    pass
