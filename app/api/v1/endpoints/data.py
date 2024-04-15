from fastapi import APIRouter


router = APIRouter()


@router.post("/data/parse")
async def parse():
    pass


@router.get("/data/status/{task_id}")
async def status():
    pass
