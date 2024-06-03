from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.db.session import get_session
from sqlalchemy.future import select
from app.api.schemas.user import UserCreate, UserLogin, User
from app.api.services.api import Api
from langchain.schema import HumanMessage
from langchain.chat_models.gigachat import GigaChat
from app.api.core.config import settings
from app.api.models.vk_api import Hint
import re
from app.api.services.user_service import get_vk_main_photo
from app.api.services.user_service import (
    create_user,
    login_user,
    create_access_token,
    get_current_user,
)
from app.api.core.config import settings
from pydantic import BaseModel


router = APIRouter()


class PromptRequest(BaseModel):
    promt: str
    user_id: int


class Req(BaseModel):
    token: str


@router.post("/get_id", response_model=dict)
async def get_user_id(user: UserCreate, db: AsyncSession = Depends(get_session)):
    pass


@router.post("/user_info/{user_id}", response_model=dict)
async def get_user_info(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id, access_token)
    try:
        data = await api.vk_user_info(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gifts_info/{user_id}")
async def get_gifts_info(
    user_id: str, token: Req, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id=user_id, token=token.token)
    user_id = await Api.get_user_id_by_name(api, user_id)
    print(user_id)
    print(type(user_id))
    result = await db.execute(select(Hint).where(Hint.id == user_id))
    print(result)
    hint = result.scalars().first()
    if not hint:
        raise HTTPException(status_code=404, detail="User not found in the database")
    try:
        api1 = Api(user_id=user_id, token=token.token)
        gifts_info = await api1.vk_gifts_info(db)
        return {"response": gifts_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wall_posts/{user_id}")
async def get_wall_posts(
    user_id: str, access_token: str, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id=user_id, token=access_token)
    try:
        data = await api.vk_wall_posts(db)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


chat = GigaChat(credentials=settings.GIGACHAT_API_KEY, verify_ssl_certs=False)


@router.post("/gifts_count/{user_id}")
async def get_gifts_count(
    user_id: str, token: Req, db: AsyncSession = Depends(get_session)
):
    api = Api(user_id=user_id, token=token.token)
    user_id = await Api.get_user_id_by_name(api, user_id)
    print(user_id)
    result = await db.execute(select(Hint).where(Hint.id == user_id))
    print(result)
    hint = result.scalars().first()
    if not hint:
        raise HTTPException(status_code=404, detail="User not found in the database")
    vk_service = Api(user_id=user_id, token=access_token)
    try:
        gifts_count = await vk_service.vk_gifts_count(db)
        return {"gift_count": gifts_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/short_content/{user_id}")    
async def gigachat_short_content(user_id: str, token: Req, db: AsyncSession = Depends(get_session)):
    """
    Эта функция взаимодействует с моделью GigaChat для создания короткого контента на основе данных пользователя.

    Parameters:
    promt_request (PromptRequest): Входной запрос, содержащий текст и ID пользователя.

    Returns:
    str: Сгенерированный контент на основе данных пользователя.

    Raises:
    HTTPException: Если данные пользователя не найдены или возникает ошибка взаимодействия с моделью GigaChat.
    """
    try:
        api = Api(user_id=user_id, token=token.token)
        user_id = await Api.get_user_id_by_name(api, user_id)
        print(user_id)
        result = await db.execute(select(Hint).where(Hint.id == user_id))
        print(result)
        hint = result.scalars().first()
        if not hint:
            raise HTTPException(
                status_code=404, detail="User not found in the database"
            )

        prompt = f"Ты — профессиональный психолог с опытом описания человека по его характеристикам. Для генерации описания человека ты изучаешь потенциальную целевую аудиторию и оптимизируешь свои навыки так, чтобы они наиболее точно раскрывали харктер человека. Создай текст описания человека с привлекающим внимание заголовком и убедительным описанием, который максимально описывает его по критериям.\n\nДанные пользователя:\nПолное имя: {hint.full_name}\nПол: {hint.sex}\nДата рождения: {hint.bdate}\nГород: {hint.city}\nОбразование: {hint.education}\nФакультет: {hint.faculty}"

        response = (
            chat([HumanMessage(content=prompt)])
            .content.replace("\n", " ")
            .replace("/", "")
            .replace('"', "")
            .replace('"Заголовок: ', "")
            .replace("Заголовок:", "")
            .replace("Описание:", "")
        )
        cleaned_text = re.sub(r"\s+", " ", response)
        hint.description = cleaned_text
        db.add(hint)
        await db.commit()
        return cleaned_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health")
async def health(user_id: str, access_token: Req):
    print(
        "udsfsdffsdfsdfsdfsdfsdfdfsFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
    )
    api = Api(user_id, access_token.token)
    user_id = await api.get_user_id_by_name(user_id)
    print(type(user_id), print(user_id))
    return await get_vk_main_photo(access_token.token, user_id)
