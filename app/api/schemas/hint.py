from pydantic import BaseModel



class Hint(BaseModel):
    vk_token: str
    hint_id: str