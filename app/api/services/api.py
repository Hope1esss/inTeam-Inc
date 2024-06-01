import os
import asyncio
import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy.future import select

from app.api.db.session import get_session
from app.api.models.vk_api import Post, Hint


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
            print("check")
            existing_user = await db.get(Hint, user_data["id"])
            print("Godo")
            if existing_user:
                print(
                    f"Пользователь {self.user_id} уже существует в базе данных."
                )
            else:
                new_hint = Hint(
                    id=user_data["id"],
                    sex=user_data["sex"],
                    bdate=user_data.get("bdate"),
                    city=user_data.get("city", {}).get("title"),
                    education=user_data.get("university_name"),
                )
                db.add(new_hint)
                await db.commit()
                print(f"Пользователь {self.user_id} сохранен в базу данных.")
            return user_data

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


# async def main():
#     user_id = "id264457326"  # Укажите ID пользователя
#     api = Api(user_id)
#     await Api.async_db_setup()
#     await api.vk_user_info()
#     await api.vk_wall_posts()
#     # Примерчик:
#     # user_id = "we1lman"  # Укажите ID пользователя
#     # api = Api(user_id)
#     # await Api.async_db_setup()
#     # await api.vk_user_info()
#     # await api.vk_wall_posts()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
