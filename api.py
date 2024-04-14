import os
import csv
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()


class Api:
    def __init__(self, id):
        self.id = id
        self.token = os.getenv("TOKEN")

    def vk_user_info(self):
        version = 5.89
        user_ids = self.id
        ru = 0
        # fields = "activities,about,blacklisted,blacklisted_by_me,books,bdate,can_be_invited_group,
        # can_post,can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,
        # career,common_count,connections,contacts,city,country,crop_photo,domain,education,exports,
        # followers_count,friend_status,has_photo,has_mobile,home_town,photo_100,photo_200,
        # photo_200_orig,photo_400_orig,photo_50,sex,site,schools,screen_name,status,verified,games,
        # interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,maiden_name,military,movies,
        # music,nickname,occupation,online,personal,photo_id,photo_max,photo_max_orig,quotes,relation,
        # relatives,timezone,tv,universities"
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
        version = 5.137
        user_id = self.id
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

    def data_base_writer(self, id, sex, date_of_birth, city, education):
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
            data_tuple = (id, sex, date_of_birth, city, education)
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


user1 = Api(os.getenv("ID"))
user1.vk_posts_exporter()
