from typing import List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Application Settings
    PROJECT_NAME: str = "Document Signature SaaS"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File Storage
    STORAGE_BASE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 20

    @computed_field
    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Email Settings
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM_EMAIL: Optional[str] = None

    # Scheduler Settings
    SCHEDULER_ENABLED: bool = True

    # Business Rules
    MAX_SIGNERS_PER_DOCUMENT: int = 15

settings = Settings()
