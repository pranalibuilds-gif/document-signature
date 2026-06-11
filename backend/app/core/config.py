from typing import Optional, Literal
import logging
from pydantic import field_validator, computed_field, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # --- Application Settings ---
    PROJECT_NAME: str = "Document Signature SaaS"
    VERSION: str = "0.1.0"
    # Literal helps enforce valid environments
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # --- Database Settings ---
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # --- JWT & Security Settings ---
    # No default value - application will fail to start if not provided
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info: ValidationInfo) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long for security.")
        return v

    # --- File Storage ---
    STORAGE_BASE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE_MB: int = 20

    @computed_field
    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # --- Email Settings ---
    MAIL_PROVIDER: Literal["mailtrap", "resend", "mock"] = "mailtrap"
    MAIL_SERVER: Optional[str] = None
    MAIL_PORT: Optional[int] = None
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM_EMAIL: Optional[str] = "noreply@docusign-mini.com"

    # Provider-specific keys (Required if that provider is chosen)
    RESEND_API_KEY: Optional[str] = None
    MAILTRAP_API_TOKEN: Optional[str] = None

    # --- Scheduler Settings ---
    SCHEDULER_ENABLED: bool = True

    # --- Business Rules ---
    MAX_SIGNERS_PER_DOCUMENT: int = 15
    SIGNING_TOKEN_EXPIRY_DAYS: int = 30
    EMAIL_VERIFICATION_EXPIRY_HOURS: int = 24

    # --- Production Safety Logic ---
    @field_validator("DEBUG", mode="after")
    @classmethod
    def enforce_prod_security(cls, v: bool, info: ValidationInfo) -> bool:
        if info.data.get("ENVIRONMENT") == "production":
            if v is True:
                logging.warning("DEBUG mode is enabled while ENVIRONMENT is production! Disabling...")
                return False
        return v

    @field_validator("MAIL_PROVIDER")
    @classmethod
    def validate_mail_config(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get("ENVIRONMENT") == "production" and v == "mock":
            raise ValueError("MAIL_PROVIDER cannot be 'mock' in production environment.")
        return v

settings = Settings()
