"""
Database configuration and session management.
Uses SQLAlchemy with asyncpg for high-performance asynchronous PostgreSQL interaction.
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# --- Database Engine ---
# SQLite requires check_same_thread=False for async use in the local development fallback.
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DEBUG, # Logs SQL queries when in development mode
    future=True,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {},
)

# --- Session Factory ---
# Produces database sessions for every request.
# expire_on_commit=False is crucial for async usage to prevent unexpected DB queries after commit.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# --- Base Model Class ---
# All models in the application must inherit from this class to be discovered by Alembic.
class Base(DeclarativeBase):
    pass
