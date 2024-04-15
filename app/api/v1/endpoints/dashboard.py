from fastapi import APIRouter


router = APIRouter()


@router.get("/dashboard/{user_id}")
async def dashboard():
    pass


@router.get("/dashboard/interests/{user_id}")
async def interests():
    pass


@router.get("/dashboard/patterns/{user_id}")
async def patterns():
    pass
