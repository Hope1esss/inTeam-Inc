import os
import requests
from dotenv import load_dotenv

load_dotenv()

# def vk_parser():
#     vk_get_main_info()
#     vk_get_wall()


def vk_get_main_info(*ids):
    token = os.getenv("TOKEN")
    version = 5.89
    user_ids = " ,".join(ids)[:-1]
    # fields = "activities,about,blacklisted,blacklisted_by_me,books,bdate,can_be_invited_group,
    # can_post,can_see_all_posts,can_see_audio,can_send_friend_request,can_write_private_message,
    # career,common_count,connections,contacts,city,country,crop_photo,domain,education,exports,
    # followers_count,friend_status,has_photo,has_mobile,home_town,photo_100,photo_200,
    # photo_200_orig,photo_400_orig,photo_50,sex,site,schools,screen_name,status,verified,games,
    # interests,is_favorite,is_friend,is_hidden_from_feed,last_seen,maiden_name,military,movies,
    # music,nickname,occupation,online,personal,photo_id,photo_max,photo_max_orig,quotes,relation,
    # relatives,timezone,tv,universities"
    fields = "activities,about"
    response = requests.get(
        "https://api.vk.com/method/users.get",
        params={
            "access_token": token,
            "v": version,
            "user_ids": user_ids,
            "fields": fields,
        },
        timeout=100,
    )

    data = response.json()
    for i, v in enumerate(ids):
        print(f"Имя пользователя: {v}")
        print(f"Имя: {data['response'][i]['first_name']}")
        print(f"Фамилия: {data['response'][i]['last_name']}")
        print(f"Id: {data['response'][i]['id']}")
        print("******************************************")
    return data


def vk_get_wall(id):
    token = os.getenv("TOKEN")
    version = 5.137
    user_id = id
    offset = 0
    count_of_wall = 100
    post_type = "all"
    additional_fields = 1  # 1 = True, 0 = False
    #  1 — в ответе будут возвращены дополнительные поля profiles и groups,
    # содержащие информацию о пользователях и сообществах. По умолчанию: 0.
    additional_fields_params = "id"
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
            "offset": dat,
        },
        timeout=100,
    )
    data = response.json()["response"]["items"]
