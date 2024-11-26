from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    DATABASE_NAME: str | None = None
    SECRET_KEY : str | None = None

    model_config = SettingsConfigDict(env_file=".env")
