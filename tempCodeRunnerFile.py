from langchain.schema import HumanMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.chat_models.gigachat import GigaChat


class StreamHandler(BaseCallbackHandler):
    def __init__(self, initial_text=""):
        pass

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(f"{token} -", end="", flush=True)


chat = GigaChat(
    credentials="M2Q5OGQ3MjAtNmZmMC00NTIyLWIzNTktYzRjNDgyZTQyZmQ5OmUzNTNkNTJmLTBhZDYtNDQ5NS1hM2Y2LWIyZTI3NDliMjgxNw==",
    streaming=False,
    callbacks=[StreamHandler()],
    verify_ssl_certs=False,
)

chat([HumanMessage(content="Напиши краткое содержание романа Евгений Онегин")])
