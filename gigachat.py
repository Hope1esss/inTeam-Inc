import json
import uuid
import httpx
import asyncio


async def get_token(auth_token, scope="GIGACHAT_API_PERS"):
    """
    Выполняет POST-запрос к эндпоинту, который выдает токен.

    Параметры:
    - auth_token (str): токен авторизации, необходимый для запроса.
    - область (str): область действия запроса API. По умолчанию — «GIGACHAT_API_PERS».

    Возвращает:
    - ответ API, где токен и срок его "годности".
    """
    # Создадим идентификатор UUID (36 знаков)
    rq_uid = str(uuid.uuid4())

    # API URL
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    # Заголовки
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": rq_uid,
        "Authorization": f"Basic {auth_token}",
    }

    # Тело запроса
    payload = {"scope": scope}

    try:
        # Делаем POST запрос с отключенной SSL верификацией
        # (можно скачать сертификаты Минцифры, тогда отключать проверку не надо)
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=headers, data=payload)
        print (response)
        return response
    except httpx.RequestError as e:
        print(f"Ошибка: {str(e)}")
        return -1


async def get_chat_completion(auth_token, user_message):
    """
    Отправляет POST-запрос к API чата для получения ответа от модели GigaChat.

    Параметры:
    - auth_token (str): Токен для авторизации в API.
    - user_message (str): Сообщение от пользователя, для которого нужно получить ответ.

    Возвращает:
    - str: Ответ от API в виде текстовой строки.
    """
    # URL API, к которому мы обращаемся
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Подготовка данных запроса в формате JSON
    payload = json.dumps(
        {
            "model": "GigaChat",  # Используемая модель
            "messages": [
                {
                    "role": "user",  # Роль отправителя (пользователь)
                    "content": user_message,  # Содержание сообщения
                }
            ],
            "temperature": 2,  # Температура генерации
            "top_p": 0.1,  # Параметр top_p для контроля разнообразия ответов
            "n": 1,  # Количество возвращаемых ответов
            "stream": False,  # Потоковая ли передача ответов
            "max_tokens": 512,  # Максимальное количество токенов в ответе
            "repetition_penalty": 1,  # Штраф за повторения
            "update_interval": 0,  # Интервал обновления (для потоковой передачи)
        }
    )

    # Заголовки запроса
    headers = {
        "Content-Type": "application/json",  # Тип содержимого - JSON
        "Accept": "application/json",  # Принимаем ответ в формате JSON
        "Authorization": f"Bearer {auth_token}",  # Токен авторизации
    }

    # Выполнение POST-запроса и возвращение ответа
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(url, headers=headers, data=payload)
        return response
    except httpx.RequestError as e:
        # Обработка исключения в случае ошибки запроса
        print(f"Произошла ошибка: {str(e)}")
        return -1


async def main():
    response = await get_token(
        "M2Q5OGQ3MjAtNmZmMC00NTIyLWIzNTktYzRjNDgyZTQyZmQ5OjZkNWYyMmQ2LTNmYjUtNGM0Ni04NTk3LWVmMTkwZDNmMjRmMw=="
    )
    if response != -1:
        print(response.text)
        giga_token = response.json()["access_token"]

        answer = await get_chat_completion(
            giga_token,
            "Что ты скажешь о человеке, предположи его интересы по таким данным: мужской пол, москва, 213 друзей в ВК, 21 год, МАИ, 8 кафедра. Напиши про него ещё информацию. Выполни ответ как можно подробнее.",
        )
        if answer != -1:
            answer_content = answer.json()["choices"][0]["message"]["content"]
            print(answer_content)


# Запуск асинхронного основного процесса
asyncio.run(main())
