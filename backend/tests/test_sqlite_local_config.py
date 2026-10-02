import os
import uuid

import pytest

from app.core.config import Settings
from app.core.database import AsyncSessionLocal, initialize_database
from app.modules.auth.service import AuthService
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate


@pytest.mark.asyncio
async def test_email_verification_works_with_sqlite_datetime_values():
    email = f"sqlite-timezone-check-{uuid.uuid4().hex[:8]}@example.com"
    await initialize_database()

    async with AsyncSessionLocal() as session:
        auth = AuthService(session)
        user = await auth.register(
            UserCreate(
                email=email,
                password="StrongPass123!",
                first_name="SQLite",
                last_name="Check",
                role="USER",
            )
        )

        await auth.verify_email(user._verification_token)
        await session.commit()

        refreshed_user = await session.get(User, user.id)
        assert refreshed_user is not None
        assert refreshed_user.is_verified is True


def test_sqlite_fallback_is_used_for_local_development(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///./local_dev.db")
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_DB", "docu_sign_db")
    monkeypatch.setenv("SECRET_KEY", "a_very_secure_local_secret_key_value_123")

    settings = Settings()

    assert settings.SQLALCHEMY_DATABASE_URI == "sqlite+aiosqlite:///./local_dev.db"


def test_sqlite_fallback_is_default_when_postgres_is_not_configured(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a_very_secure_local_secret_key_value_123")
    monkeypatch.setenv("POSTGRES_SERVER", "")
    monkeypatch.setenv("POSTGRES_USER", "")
    monkeypatch.setenv("POSTGRES_PASSWORD", "")
    monkeypatch.setenv("POSTGRES_DB", "")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = Settings()

    assert settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite+aiosqlite")
