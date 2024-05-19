"""
Этот модуль предназначен для взаимодействия с API ВКонтакте и работы с данными пользователей.
Он предоставляет класс `Api`, который позволяет:

*   Получать информацию о пользователе, такую как ID, пол, дата рождения, город и образование.
*   Получать список записей со стены пользователя,
включая количество лайков, просмотров, текст,
URL-адреса изображений и аудиозаписей.
*   Экспортировать данные о записях пользователя в CSV-файл.
*   Записывать информацию о пользователе в базу данных SQLite.

Пример использования:

```python
api = Api(user_id='1234567')  # Замените '1234567' на реальный ID пользователя

# Получить информацию о пользователе и записать ее в базу данных
api.vk_user_info()

# Получить список записей со стены пользователя
posts = api.vk_wall_posts()

# Экспортировать данные о записях в CSV-файл
api.vk_posts_exporter()
"""

import os
import aiofiles
import csv
import sqlite3
import asyncio
import httpx
import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, select
from dotenv import load_dotenv

load_dotenv()


class Api:
    """
    Класс для работы с API ВКонтакте и данными пользователей.

    Attributes
    ----------
    user_id : str
        ID пользователя ВКонтакте.
    token : str
        Токен доступа к API ВКонтакте.

    Methods
    -------
    vk_user_info()
        Получает информацию о пользователе из API ВКонтакте и записывает ее в базу данных SQLite.
    vk_wall_posts()
        Получает список записей со стены пользователя ВКонтакте.
    vk_posts_exporter()
        Экспортирует данные о записях пользователя ВКонтакте в CSV-файл.
    data_base_writer(user_id, sex, date_of_birth, city, education)
        Записывает информацию о пользователе в базу данных SQLite.
    """

    def __init__(self, user_id):
        """
        Инициализирует объект класса `Api`.

        Parameters
        ----------
        user_id : str
            ID пользователя ВКонтакте.
        """
        self.user_id = user_id
        self.token = os.getenv(
            "TOKEN"
        )  # Получает токен доступа из переменной окружения

    async def vk_user_info(self):
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
                        "lang": 0
                    }
                )
            response.raise_for_status()  # Проверка на наличие HTTP ошибок
            data = response.json()["response"][0]
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        else:
            async with async_session() as session:
                new_user = User(
                    id=data["id"],
                    sex=data["sex"],
                    bdate=data.get("bdate"),
                    city=data.get("city", {}).get("title"),
                    education=data.get("university_name")
                )
                session.add(new_user)
                await session.commit()
                print("Пользователь сохранен в базу данных.")

    async def vk_wall_posts(self):
        version = 5.137
        count_of_wall = 100
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
                    "offset": 0
                }
            )
        posts_data = response.json()["response"]["items"]

        async with async_session() as session:
            for post_data in posts_data:
                new_post = Post(
                    user_id=self.user_id,
                    text=post_data["text"],
                    likes=post_data["likes"]["count"],
                    views=post_data.get("views", {}).get("count", 0),
                    img_url=", ".join(
                        [attachment["photo"]["sizes"][-1]["url"] for attachment in post_data.get("attachments", []) if
                         attachment["type"] == "photo"]),
                    audio_url=", ".join(
                        [attachment["audio"]["url"] for attachment in post_data.get("attachments", []) if
                         attachment["type"] == "audio"])
                )
                session.add(new_post)
            await session.commit()
            print("Записи сохранены в базу данных.")

    async def vk_posts_exporter(self):
        async with async_session() as session:
            result = await session.execute(select(Post))
            posts = result.scalars().all()

        async with aiofiles.open("posts.csv", "w", newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['text', 'likes', 'views', 'img_url', 'audio_url'])
            await csvfile.write(writer.writeheader())
            for post in posts:
                await csvfile.write(writer.writerow({
                    'text': post.text,
                    'likes': post.likes,
                    'views': post.views,
                    'img_url': post.img_url,
                    'audio_url': post.audio_url
                }))
        print("Данные о записях экспортированы в CSV-файл.")

    async def async_db_setup():
        """Асинхронное создание таблицы в базе данных, если она не существует."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def data_base_writer(user_id, sex, date_of_birth, city, education):
        try:
            async with async_session() as session:
                new_user = User(
                    id=user_id,
                    sex=sex,
                    bdate=date_of_birth,
                    city=city,
                    education=education
                )
                session.add(new_user)
                await session.commit()
                print("Данные пользователя успешно сохранены.")
        except Exception as e:
            print(f"Database error occurred: {e}")


api = Api("id264457326")
asyncio.run(api.vk_user_info())
