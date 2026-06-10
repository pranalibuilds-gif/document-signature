import asyncio
from sqlalchemy import text
from app.core.database import engine, AsyncSessionLocal

async def test_connection():
    print("Testing database connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection successful! Result: {result.fetchone()}")

        async with AsyncSessionLocal() as session:
            print("Session creation successful!")

    except Exception as e:
        print(f"Connection failed: {e}")
        print("\nNote: Make sure PostgreSQL is running and the database 'docu_sign_db' exists.")

if __name__ == "__main__":
    asyncio.run(test_connection())
