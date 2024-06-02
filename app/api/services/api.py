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

from app.api.models.vk_api import Post, Hint, GiftInfo, GiftCount


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

    async def vk_gifts_info(self, db: AsyncSession):
        version = 5.89
        from_id_count = {}
        count = 1_000
        offset = 0
        total_gifts = 0

        try:
            async with httpx.AsyncClient() as client:
                while True:
                    response = await client.get(
                        "https://api.vk.com/method/gifts.get",
                        params={
                            "access_token": self.token,
                            "v": version,
                            "user_id": self.user_id,
                            "count": count,
                            "offset": offset,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                    print("Full response:", data)
                    if "error" in data:
                        raise ValueError(f"API error: {data['error']['error_msg']}")

                    gifts_data = data.get("response", {}).get("items", [])
                    total_gifts += len(gifts_data)
                    print(f"Total gifts processed so far: {total_gifts}")

                    if not gifts_data:
                        break

                    for gift in gifts_data:
                        from_id = gift.get("from_id")
                        if from_id is not None:
                            if from_id in from_id_count:
                                from_id_count[from_id] += 1
                            else:
                                from_id_count[from_id] = 1

                    offset += count

                for from_id, count in from_id_count.items():
                    existing_gift = await db.execute(
                        select(GiftInfo).where(GiftInfo.user_id == self.user_id, GiftInfo.from_id == from_id)
                    )
                    existing_gift = existing_gift.scalar()
                    if existing_gift:
                        existing_gift.from_id_count = count
                    else:
                        new_gift = GiftInfo(
                            user_id=self.user_id,
                            from_id=from_id,
                            from_id_count=count
                        )
                        db.add(new_gift)
                await db.commit()
                print(f"Количество подарков для пользователя {self.user_id} сохранено в базу данных.")

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        sorted_from_id_count = dict(sorted(from_id_count.items(), key=lambda item: item[1], reverse=True))

        print(f"Total gifts received: {total_gifts}")
        return sorted_from_id_count, len(from_id_count), sum(from_id_count.values())

    async def vk_gifts_count(self, db: AsyncSession):
        version = 5.89
        gift_count = 0
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.vk.com/method/gifts.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "user_id": self.user_id,
                        "count": 20_000,  # wHy limit 19_175?? or 19_168???
                    },
                )
            response.raise_for_status()
            data = response.json()

            print("Full response:", data)
            if "error" in data:
                raise ValueError(f"API error: {data['error']['error_msg']}")

            gifts_data = data.get("response", {}).get("items", [])
            gift_count = len(gifts_data)

            existing_gift_count = await db.get(GiftCount, self.user_id)
            if existing_gift_count:
                existing_gift_count.count = gift_count
            else:
                new_gift_count = GiftCount(user_id=self.user_id, count=gift_count)
                db.add(new_gift_count)

            await db.commit()
            print(
                f"Количество подарков для пользователя {self.user_id} сохранено в базу данных: {gift_count}"
            )

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except httpx.ConnectTimeout:
            print("The request timed out while trying to connect to the remote server.")
        except httpx.ReadTimeout:
            print("The server did not send any data in the allotted amount of time.")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return gift_count

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
#     token = os.getenv("TOKEN")  # Убедитесь, что токен загружен из переменной окружения
#     api = Api(user_id, token)

#     # Пример использования сессии базы данных
#     async with async_session() as session:
#         await api.vk_user_info(session)
#         await api.vk_wall_posts(session)
#         await api.analyze_with_gigachat(session, user_id)  # Вызов функции для получения данных из Gigachat


# if __name__ == "__main__":
#     asyncio.run(main())
