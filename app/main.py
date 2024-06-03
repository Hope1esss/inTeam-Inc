from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.core.config import settings
from app.api.db.init_db import create_db_and_tables
from app.api.v1.endpoints import router as api_v1_router
from app.api.services.user_service import get_vk_main_photo
from app.api.services.api import Api

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


@app.get('/health')
async def health(user_id: str, access_token: str):
    print('udsfsdffsdfsdfsdfsdfsdfdfsFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
    api = Api(user_id, access_token)
    user_id = await api.get_user_id_by_name(user_id)
    print(type(user_id), print(user_id))
    return await get_vk_main_photo(access_token, user_id)