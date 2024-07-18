import os
import secrets
from typing import Literal

from pydantic_settings import BaseSettings

import dotenv

dotenv.load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = f"FlatSharing Community"
    DESCRIPTION: str = "FlatSharing Backend"
    ENV: Literal["development", "staging", "production"] = "production"
    VERSION: str = "0.1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DATABASE_URI: str = os.getenv('DATABASE_URI')#"postgresql://postgres@localhost:5432/postgres"

    class Config:
        case_sensitive = True


settings = Settings()


class TestSettings(Settings):
    class Config:
        case_sensitive = True


test_settings = TestSettings()
