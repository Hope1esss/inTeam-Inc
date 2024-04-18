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
import csv
import sqlite3
import asyncio
import httpx
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
        """
        Получает информацию о пользователе из API ВКонтакте и записывает ее в базу данных SQLite.

        Информация включает в себя ID, пол, дату рождения, город и информацию об образовании.
        """
        version = 5.89
        user_ids = self.user_id
        ru = 0  # Устанавливает язык ответа на русский
        fields = (
            "sex,bdate,city,education"  # Запрашиваемые поля информации о пользователе
        )

        async with httpx.AsyncClient() as client:
            response = (
                await client.get(  # Отправляет асинхронный запрос к API ВКонтакте
                    "https://api.vk.com/method/users.get",
                    params={
                        "access_token": self.token,
                        "v": version,
                        "user_ids": user_ids,
                        "fields": fields,
                        "lang": ru,
                    },
                    timeout=100,
                )
            )

        data = response.json()["response"][0]  # Извлекает данные из JSON-ответа

        # Извлекает необходимые данные из ответа
        id_data = data["id"]
        sex_data = data["sex"]
        bdate_data = data.get(
            "bdate", None
        )  # Если дата рождения не указана, возвращает None
        city_data = data.get("city", {}).get(
            "title", None
        )  # Если город не указан, возвращает None
        university_name_data = data.get("university_name", None)

        # Вызывает метод data_base_writer для записи данных в базу данных
        self.data_base_writer(
            id_data,
            sex_data,
            bdate_data,
            None if city_data == "" else city_data,
            None if university_name_data == "" else university_name_data,
        )

    async def _vk_wall_posts(self):
        """
        Получает список записей со стены пользователя ВКонтакте.

        Returns
        -------
        list
            Список словарей, содержащих информацию о каждой записи на стене.
        """
        version = 5.137
        user_id = self.user_id
        count_of_wall = 100  # Количество запрашиваемых записей
        post_type = "all"  # Тип записей (все)
        additional_fields = 1  # Включает дополнительные поля profiles и groups в ответе
        additional_fields_params = "id"  # Запрашиваемые дополнительные поля
        all_posts = []
        offset = 0  # Смещение для получения следующих записей

        async with httpx.AsyncClient() as client:
            # Отправляет запрос к API ВКонтакте
            response = await client.get(
                "https://api.vk.com/method/wall.get",
                params={
                    "access_token": self.token,
                    "v": version,
                    "owner_id": user_id,
                    "count": count_of_wall,
                    "filter": post_type,
                    "extended": additional_fields,
                    "fields": additional_fields_params,
                    "offset": offset,
                },
                timeout=100,
            )
            data = response.json()["response"][
                "items"
            ]  # Извлекает данные из JSON-ответа
            all_posts.extend(data)  # Добавляет полученные записи в список
        return all_posts  # Возвращает список записей

    def vk_posts_exporter(self):
        """
        Экспортирует данные о записях пользователя ВКонтакте в CSV-файл "file1.csv".

        Файл содержит информацию о количестве лайков, просмотров, тексте записи, URL-адресах
        изображений и аудиозаписей.
        """
        # os.remove("file1.csv")  # Удаляет существующий файл, если он есть

        # Открывает файл для записи
        with open("file1.csv", "w", encoding="utf-8") as file:
            pen = csv.writer(file)
            pen.writerow(
                ["likes", "views", "text", "img-url", "audio-url"]
            )  # Записывает заголовок

            # Перебирает записи на стене пользователя
            for post in self._vk_wall_posts():
                img_url = []
                audio_url = []
                for i in range(len(post["attachments"])):
                    if post["attachments"][i]["type"] == "photo":
                        img_url.append(
                            post["attachments"][i]["photo"]["sizes"][-1]["url"]
                        )
                    if post["attachments"][i]["type"] == "audio":
                        audio_url.append(post["attachments"][i]["audio"]["url"])
                    if post["text"] == "":
                        text = "None"
                    else:
                        text = post["text"]
                pen.writerow(
                    [
                        post["likes"]["count"],
                        post["views"]["count"] if "views" in post.keys() else "0",
                        text,
                        img_url,
                        audio_url,
                    ]
                )

    def data_base_writer(self, user_id, sex, date_of_birth, city, education):
        """
        Записывает информацию о пользователе в базу данных SQLite "user.db".

        Parameters
        ----------
        user_id : int
            ID пользователя.
        sex : int
            Пол пользователя (1 - женский, 2 - мужской).
        date_of_birth : str
            Дата рождения пользователя в формате DD.MM.YYYY.
        city : str
            Город пользователя.
        education : str
            Информация об образовании пользователя.

        Raises
        ------
        sqlite3.Error
            Если возникает ошибка при работе с базой данных.
        """
        try:
            database = sqlite3.connect("user.db")  # Подключается к базе данных
            cursor = database.cursor()
            print("Подключен к SQLite")

            # Создает таблицу "users", если она не существует
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
                id integer PRIMARY KEY,
                sex integer,
                bdate text,
                city text,
                education text
            )"""
            )

            # Подготавливает запрос на вставку данных
            sqlite_insert_with_param = """INSERT INTO users
                                (id, sex, bdate, city, education)
                                VALUES (?, ?, ?, ?, ?)"""
            data_tuple = (user_id, sex, date_of_birth, city, education)

            # Выполняет запрос на вставку данных
            cursor.execute(sqlite_insert_with_param, data_tuple)
            database.commit()  # Сохраняет изменения
            print("Переменные Python успешно вставлены в таблицу user.db")
            cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        finally:
            if database:
                database.close()  # Закрывает соединение с базой данных
                print("Соединение с SQLite закрыто")


api = Api("id264457326")
asyncio.run(api.vk_user_info())
