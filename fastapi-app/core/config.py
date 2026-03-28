from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"


settings = Settings()
