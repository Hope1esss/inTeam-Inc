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


from app.api.models.vk_api import Post, Hint, GiftInfo, GiftCount


from collections import OrderedDict


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

    async def get_user_names(self, user_ids):
        version = 5.89
        user_names = {}
        individual_user_ids = [user_id for user_id in user_ids if user_id > 0]
        group_ids = [user_id for user_id in user_ids if user_id < 0]

        try:
            if individual_user_ids:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.vk.com/method/users.get",
                        params={
                            "access_token": self.token,
                            "v": version,
                            "user_ids": ",".join(map(str, individual_user_ids)),
                            "fields": "first_name,last_name",
                        },
                    )
                response.raise_for_status()
                data = response.json()
                user_names.update(
                    {user['id']: f"{user['first_name']} {user['last_name']}" for user in data.get("response", [])})

            if group_ids:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.vk.com/method/groups.getById",
                        params={
                            "access_token": self.token,
                            "v": version,
                            "group_ids": ",".join(map(lambda x: str(abs(x)), group_ids)),
                            "fields": "name",
                        },
                    )
                response.raise_for_status()
                data = response.json()
                user_names.update({-group['id']: group['name'] for group in data.get("response", [])})

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return user_names

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
                        select(GiftInfo).where(
                            GiftInfo.user_id == self.user_id,
                            GiftInfo.from_id == from_id,
                        )
                    )
                    existing_gift = existing_gift.scalar()
                    if existing_gift:
                        existing_gift.from_id_count = count
                    else:
                        new_gift = GiftInfo(
                            user_id=self.user_id, from_id=from_id, from_id_count=count
                        )
                        db.add(new_gift)
                await db.commit()
                print(
                    f"Количество подарков для пользователя {self.user_id} сохранено в базу данных."
                )

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        sorted_from_id_count = sorted(from_id_count.items(), key=lambda item: item[1], reverse=True)[:5]

        user_ids = [item[0] for item in sorted_from_id_count]
        user_names = await self.get_user_names(user_ids)

        sorted_from_id_count_with_names = OrderedDict(
            (user_names.get(from_id, str(from_id)), count) for from_id, count in sorted_from_id_count
        )
        print(sorted_from_id_count_with_names)

        print(f"Total gifts received: {total_gifts}")
        return sorted_from_id_count_with_names, sum(from_id_count.values())

    async def vk_get_friend_list(self, db: AsyncSession):
        version = 5.236
        fields = "bdate,sex"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.vk.com/method/friends.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "user_id": self.user_id,
                        "fields": fields,
                        "order": "hints"
                    },
                )
            response.raise_for_status()
            data = response.json()

            print("Full response:", data)
            friend_list_data = data.get("response", {}).get("items", [])
            if not friend_list_data:
                raise ValueError("Key 'items' not found in the response")

            for friend_data in friend_list_data:
                processed_data = {
                    "full_name": friend_data.get("first_name", "")
                                 + " "
                                 + friend_data.get("last_name", ""),
                    "sex": (
                        "Мужской"
                        if friend_data.get("sex") == 2
                        else "Женский" if friend_data.get("sex") == 1 else ""
                    ),
                    "bdate": friend_data.get("bdate", "")
                }
                print("Processed data:", processed_data)

                existing_user = await db.execute(select(Hint).where(Hint.id == friend_data["id"]))
                existing_user = existing_user.scalars().first()
                if existing_user:
                    print(f"Пользователь {friend_data['id']} уже существует в базе данных.")
                else:
                    new_friends = Hint(
                        id=friend_data["id"],
                        full_name=processed_data["full_name"],
                        sex=processed_data["sex"],
                        bdate=processed_data["bdate"],
                    )
                    db.add(new_friends)
            await db.commit()
            print(f"Список друзей пользователя {self.user_id} сохранен в базу данных.")

            return friend_list_data

        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

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

    async def get_user_id_by_name(self, screen_name: str):
        version = 5.131
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.vk.com/method/users.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "user_ids": screen_name,
                        "lang": 0,
                    },
                )
            response.raise_for_status()
            data = response.json()
            print("Full response:", data)
            user_data = data.get("response", [None])[0]
            if user_data is None:
                raise ValueError("User not found")
            return int(user_data["id"])
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code}")


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
