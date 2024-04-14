"""Модуль обсепечивать импорт токена из .env файла."""
import os
import csv
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

<<<<<<< HEAD
# def vk_parser():
#     vk_get_main_info()
#     vk_get_wall()
=======

class Api:
    """
    Класс для взаимодействия с VK API.

    ...

    Атрибуты
    ----------
    user_id : str
        Идентификатор пользователя VK.
    token : str
        Токен доступа к VK API.

    Методы
    -------
    vk_user_info():
        Получает и записывает информацию о пользователе в базу данных SQLite.
    vk_wall_posts():
        Получает записи со стены пользователя VK.
    vk_posts_exporter():
        Экспортирует данные о записях в файл CSV.
    data_base_writer(user_id, sex, date_of_birth, city, education):
        Записывает информацию о пользователе в базу данных SQLite.
    """

    def __init__(self, user_id):
        """
        Инициализирует все необходимые атрибуты для объекта Api.

        Параметры
        ----------
            user_id : str
                Идентификатор пользователя VK.
        """

        self.user_id = user_id
        self.token = os.getenv("TOKEN")
>>>>>>> f4f3e6e (update)

    def vk_user_info(self):
        """
        Получает информацию о пользователе от VK API и записывает ее в базу данных SQLite.

        Информация включает в себя идентификатор пользователя, пол, дату рождения, город и образование.
        """
        version = 5.89
        user_ids = self.user_id
        ru = 0
        fields = "sex,bdate,city,education"
        response = requests.get(
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

        data = response.json()
        id_data = data["response"][0]["id"]
        sex_data = data["response"][0]["sex"]
        bdate_data = data["response"][0].get("bdate", None)
        city_data = data["response"][0].get("city", {}).get("title", None)
        university_name_data = data["response"][0]["university_name"]
        self.data_base_writer(
            id_data,
            sex_data,
            bdate_data,
            None if city_data == "" else city_data,
            None if university_name_data == "" else university_name_data,
        )

    def vk_wall_posts(self):
        """
        Получает записи со стены пользователя VK.

        Возвращает
        -------
        list
            Список словарей, каждый из которых представляет собой запись на стене пользователя VK.
        """
        version = 5.137
        user_id = self.user_id
        count_of_wall = 100
        post_type = "all"
        additional_fields = 1  # 1 = True, 0 = False
        #  1 — в ответе будут возвращены дополнительные поля profiles и groups,
        # содержащие информацию о пользователях и сообществах. По умолчанию: 0.
        additional_fields_params = "id"
        all_posts = []
        offset = 0
        response = requests.get(
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
        data = response.json()["response"]["items"]
        all_posts.extend(data)
        return all_posts

    def vk_posts_exporter(self):
        """
        Экспортирует данные о записях в файл CSV.

        Экспортируемые данные включают количество лайков, просмотров, текст, URL изображения и URL аудио каждой записи.
        """
        os.remove("file1.csv")
        with open("file1.csv", "w", encoding="utf-8") as file:
            pen = csv.writer(file)
            pen.writerow(["likes", "views", "text", "img-url", "audio-url"])
            for post in self.vk_wall_posts():
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
        Записывает информацию о пользователе в базу данных SQLite.

        Параметры
        ----------
        user_id : int
            Идентификатор пользователя VK.
        sex : int
            Пол пользователя VK. 1 для женщин, 2 для мужчин.
        date_of_birth : str
            Дата рождения пользователя VK в формате 'dd.mm.yyyy'.
        city : str
            Город пользователя VK.
        education : str
            Образование пользователя VK.
        """
        try:
            database = sqlite3.connect("user.db")
            cursor = database.cursor()
            print("Подключен к SQLite")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY,
            sex integer,
            bdate text,
            city text,
            education text
        )"""
            )
            sqlite_insert_with_param = """INSERT INTO users
                                (id, sex, bdate, city, education)
                                VALUES (?, ?, ?, ?, ?)"""
            data_tuple = (user_id, sex, date_of_birth, city, education)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            database.commit()
            print("Переменные Python успешно вставлены в таблицу user.db")
            cursor.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        finally:
            if database:
                database.close()
                print("Соединение с SQLite закрыто")
