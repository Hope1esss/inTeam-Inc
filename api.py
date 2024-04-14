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
    def __init__(self, id):
        self.id = id
        self.token = os.getenv("TOKEN")
>>>>>>> f4f3e6e (update)

    def VKUserInfo(self):
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
        id = data["response"][0]["id"]
        bdate = data["response"][0].get("bdate", None)
        city = data["response"][0].get("city", {}).get("title", None)
        university_name = data["response"][0]["university_name"]
        ret = self.DatabaseWriter(
            id,
            bdate,
            None if city == "" else city,
            None if university_name == "" else university_name,
        )
        return ret

    def VKWallPosts(self):
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
        while offset < 100:
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
            offset += 100
            all_posts.extend(data)
        return all_posts

    def VKPostsExporter(self):
        with open("file1.cvs", "w", encoding="utf-8") as file:
            pen = csv.writer(file)
            pen.writerow(["likes", "body", "url"])
            for post in self.vk_get_posts():
                try:
                    if post["attachments"][0]:
                        img_url = post["attachments"][0]["photo"]["sizes"][-1]["url"]
                    else:
                        img_url = "pass"
                except:
                    pass
                try:
                    pen.writerow([post["likes"]["count"], post["text"], img_url])
                except:
                    pass

    def DatabaseWriter(self, id, date_of_birth, city, education):
        try:
            database = sqlite3.connect("user.db")
            cursor = database.cursor()
            print("Подключен к SQLite")
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
            id integer PRIMARY KEY,
            bdate text,
            city text,
            education text
        )"""
            )
            sqlite_insert_with_param = """INSERT INTO users
                                (id, bdate, city, education)
                                VALUES (?, ?, ?, ?)"""
            data_tuple = (id, date_of_birth, city, education)
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
        return 0


user1 = Api(os.getenv("ID"))
user1.VKUserInfo()
