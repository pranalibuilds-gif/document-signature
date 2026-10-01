import os

from app.core.config import Settings


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
