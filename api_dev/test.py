import os
import requests
from dotenv import load_dotenv
import csv
import time

load_dotenv()

token = os.getenv("TOKEN")
version = 5.137
user_id = "unelzit"
count_of_wall = 100
post_type = "all"
additional_fields = 1  # 1 = True, 0 = False
#  1 — в ответе будут возвращены дополнительные поля profiles и groups,
# содержащие информацию о пользователях и сообществах. По умолчанию: 0.
additional_fields_params = "id"
all_posts = []
offset = 0
while offset < 1000:
    response = requests.get(
        "https://api.vk.com/method/wall.get",
        params={
            "access_token": token,
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
    data = response.json()
    offset += 100
    all_posts.extend(data)
    time.sleep(0.5)
print(response)
