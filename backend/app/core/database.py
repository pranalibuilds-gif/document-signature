"""Database bootstrap and shared SQLAlchemy configuration.

The project intentionally supports both Postgres for production-like setups and
SQLite for local development. This module centralizes the engine and the base
ORM model so the rest of the application can work with a single database API.
"""

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# --- Database Engine ---
# SQLite requires check_same_thread=False when using the async engine in a
# local development environment. PostgreSQL does not need this extra flag.
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DEBUG,  # Logs SQL queries when in development mode.
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {},
)

# --- Session Factory ---
# Every request gets its own async session from this factory. `expire_on_commit`
# stays disabled so data remains usable after commit during async flows and
# serialization without issuing additional database queries.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def initialize_database() -> None:
    """Creates tables for the local SQLite database when the schema is not initialized yet."""
    async with engine.begin() as connection:
        if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite"):
            tables = await connection.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
            if not tables:
                await connection.run_sync(Base.metadata.create_all)


# --- Base Model Class ---
# All models in the application inherit from this base class so SQLAlchemy can
# discover them and Alembic migrations can track schema changes consistently.
class Base(DeclarativeBase):
    pass

# Import all models so the local SQLite metadata includes the full application
# schema during initialization. This must happen after Base is defined so the
# model metadata is registered to the correct declarative base.
from app.modules import models  # noqa: E402,F401
