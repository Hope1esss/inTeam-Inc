"""Пример работы с чатом через gigachain"""

from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

# Авторизация в сервисе GigaChat
chat = GigaChat(
    credentials="M2Q5OGQ3MjAtNmZmMC00NTIyLWIzNTktYzRjNDgyZTQyZmQ5OmUzNTNkNTJmLTBhZDYtNDQ5NS1hM2Y2LWIyZTI3NDliMjgxNw==",
    verify_ssl_certs=False,
)

messages = [
    SystemMessage(
        content="Ты — профессиональный психолог с опытом описания человека по его характеристикам. Для генерации описания человека ты изучаешь потенциальную целевую аудиторию и оптимизируешь свои навыки так, чтобы они наиболее точно раскрывали харктер человека. Создай текст описания человека с привлекающим внимание заголовком и убедительным описанием, который максимально описывает его по критериям."
    )
]

user_input = input("User: ")
messages.append(HumanMessage(content=user_input))
res = chat(messages)
messages.append(res)
print(res.content)
