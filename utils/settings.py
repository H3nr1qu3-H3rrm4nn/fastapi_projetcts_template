from enum import Enum
from pydantic_settings import BaseSettings

class AppEnvironment(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class Settings(BaseSettings):

    DATABASE_URL: str = "postgresql+asyncpg://admin:tracking2025@localhost:5432/tracker"
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT

    # Configurações para JWT
    SECRET_KEY: str = "e2fc6a47b06ca21ba2cc5850927b808e8fcd9cbb979ddafe43253ff911da9644"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1

    # Configurações do aplicativo
    app_name: str = "Rastreamento API"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()