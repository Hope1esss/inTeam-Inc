import os
import asyncio
import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.future import select

from app.api.db.session import get_session
from app.api.models.vk_api import Post, Hint
from app.api.core.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
async_session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GIGACHAT_PROMPT = (
    "Я предоставлю тебе данные человека, напиши что ты думаешь о его интересах: "
    "{full_name}, {sex}, {bdate}, {city}, {education}, {faculty}"
)


class Api:
    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    async def vk_user_info(self, db: AsyncSession):
        version = 5.89
        fields = "sex,bdate,city,education"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.vk.com/method/users.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "user_ids": self.user_id,
                        "fields": fields,
                        "lang": 0,
                    },
                )
            response.raise_for_status()
            data = response.json()

            print("Full response:", data)
            user_data = data.get("response", [None])[0]
            if user_data is None:
                raise ValueError("Key 'response' not found in the response")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        else:
            processed_data = {
                "full_name": user_data.get("first_name", "")
                + " "
                + user_data.get("last_name", ""),
                "sex": (
                    "Мужской"
                    if user_data.get("sex") == 2
                    else "Женский" if user_data.get("sex") == 1 else ""
                ),
                "bdate": user_data.get("bdate", ""),
                "city": user_data.get("city", {}).get("title", ""),
                "education": user_data.get("university_name", ""),
                "faculty": user_data.get("faculty_name", ""),
            }
            print("Processed data:", processed_data)

            existing_user = await db.get(Hint, user_data["id"])
            if existing_user:
                print(f"Пользователь {self.user_id} уже существует в базе данных.")
            else:
                new_hint = Hint(
                    id=user_data["id"],
                    full_name=processed_data["full_name"],
                    sex=processed_data["sex"],
                    bdate=processed_data["bdate"],
                    city=processed_data["city"],
                    education=processed_data["education"],
                    faculty=processed_data["faculty"],
                )
                db.add(new_hint)
                await db.commit()
                print(f"Пользователь {self.user_id} сохранен в базу данных.")
            return data

    async def vk_wall_posts(self, db: AsyncSession):
        version = 5.137
        count_of_wall = 100
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.vk.com/method/wall.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "owner_id": self.user_id,
                        "count": count_of_wall,
                        "filter": "all",
                        "extended": 1,
                        "fields": "id",
                        "offset": 0,
                    },
                )
            response.raise_for_status()
            data = response.json()
            print("Full response from wall.get:", data)
            posts_data = data.get("response", {}).get("items", [])
            if not posts_data:
                raise ValueError("Key 'items' not found in the response")
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        else:
            for post_data in posts_data:
                new_post = Post(
                    user_id=self.user_id,
                    text=post_data.get("text", ""),
                    likes=post_data.get("likes", {}).get("count", 0),
                    views=post_data.get("views", {}).get("count", 0),
                    img_url=", ".join(
                        [
                            attachment["photo"]["sizes"][-1]["url"]
                            for attachment in post_data.get("attachments", [])
                            if attachment["type"] == "photo"
                        ]
                    ),
                    audio_url=", ".join(
                        [
                            attachment["audio"]["url"]
                            for attachment in post_data.get("attachments", [])
                            if attachment["type"] == "audio"
                        ]
                    ),
                )
                db.add(new_post)
            await db.commit()
            print(f"Записи пользователя {self.user_id} сохранены в базу данных.")
        return posts_data

    async def analyze_with_gigachat(self, db: AsyncSession, user_id: int):
        async with db.begin():
            result = await db.execute(select(Hint).where(Hint.id == user_id))
            hint = result.scalars().first()
            if not hint:
                raise ValueError("User not found in the database")
            
            prompt = GIGACHAT_PROMPT.format(
                full_name=hint.full_name,
                sex=hint.sex,
                bdate=hint.bdate,
                city=hint.city,
                education=hint.education,
                faculty=hint.faculty
            )

            payload = {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 1,
                "top_p": 0.1,
                "n": 1,
                "stream": False,
                "max_tokens": 512,
                "repetition_penalty": 1
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    GIGACHAT_API_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {settings.GIGACHAT_API_KEY}"
                    }
                )
                response.raise_for_status()
                gigachat_data = response.json()
                print("Gigachat response:", gigachat_data)
                return gigachat_data["choices"][0]["message"]["content"]


# async def main():
#     user_id = "id264457326"  # Укажите ID пользователя
#     token = os.getenv("TOKEN")  # Убедитесь, что токен загружен из переменной окружения
#     api = Api(user_id, token)

#     # Пример использования сессии базы данных
#     async with async_session() as session:
#         await api.vk_user_info(session)
#         await api.vk_wall_posts(session)
#         await api.analyze_with_gigachat(session, user_id)  # Вызов функции для получения данных из Gigachat


# if __name__ == "__main__":
#     asyncio.run(main())
