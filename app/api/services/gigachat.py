from langchain.schema import HumanMessage
from langchain_community.chat_models import GigaChat
from fastapi import APIRouter, HTTPException
from app.api.core.config import settings

chat = GigaChat(credentials=settings.GIGACHAT_API_KEY, verify_ssl_certs=False)


def gigachat_short_content(query: str):
    try:
        prompt = "Привет! Я GigaChat, и я здесь, чтобы помочь вам с созданием контента."
        return chat([HumanMessage(content=prompt)])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
