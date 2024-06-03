from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.core.config import settings
from app.api.db.init_db import create_db_and_tables
from app.api.v1.endpoints import router as api_v1_router

from app.api.services.api import Api
from app.api.v1.endpoints.user import Req

app = FastAPI(
    title="My Project",
    description="This is a sample project",
    version="1.0.0",
    docs_url="/api/v1/docs",  # Swagger UI
    redoc_url="/api/v1/redoc",  # ReDoc UI
    openapi_url="/api/v1/openapi.json"  # OpenAPI schema
)

# Подключение маршрутизатора с префиксом /api/v1
app.include_router(api_v1_router, prefix="/api/v1")

# Настройка CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await create_db_and_tables()


