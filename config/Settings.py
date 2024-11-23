from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    DATABASE_NAME: Optional[str] = None
    
    class Config:
        env_file = ".env"