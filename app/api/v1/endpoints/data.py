# from fastapi import APIRouter, Depends
# from app.api.db.init_db import User
# from .auth import fastapi_users
#
#
# router = APIRouter()
#
#
# @router.post("/data/parse")
# async def parse(user: User = Depends(fastapi_users.current_user())):
#     return {"message": f"{user}"}
#
#
# @router.get("/data/status/{task_id}")
# async def status():
#     pass
