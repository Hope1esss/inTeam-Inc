from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    base_token: str
    reset_password_token_secret: str
    verification_token_secret: str

    class Config:
        env_file = "need.env"


settings = Settings()
