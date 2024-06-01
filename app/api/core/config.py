from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str
    SITE: str

    class Config:
        env_file = "need.env"


settings = Settings()
