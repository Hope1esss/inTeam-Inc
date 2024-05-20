from pydantic import BaseModel


class Token(BaseModel):
    access_token: str

    class Config:
        from_attributes = True
