import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def create_db():
    # Connect to the default 'postgres' database to create the new one
    admin_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")

    print(f"Attempting to create database: {settings.POSTGRES_DB}")
    async with engine.connect() as conn:
        try:
            await conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
            print(f"Database {settings.POSTGRES_DB} created successfully!")
        except Exception as e:
            if "already exists" in str(e):
                print(f"Database {settings.POSTGRES_DB} already exists.")
            else:
                print(f"Failed to create database: {e}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_db())
