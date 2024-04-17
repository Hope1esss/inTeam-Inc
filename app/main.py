from fastapi import FastAPI

from app.api.db.init_db import create_db_and_tables
from app.api.v1.endpoints import router as api_v1_router


app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()