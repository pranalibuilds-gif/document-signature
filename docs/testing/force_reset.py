import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.core.security.hashing import hash_password
from app.common.enums import UserRole
from sqlalchemy import text

async def reset():
    async with AsyncSessionLocal() as s:
        print("Emptying database...")
        await s.execute(text('TRUNCATE TABLE users CASCADE'))

        print("Creating fresh demo account...")
        u = User(
            email='pranali@demo.com',
            hashed_password=hash_password('Pranali123!'),
            first_name='Pranali',
            last_name='Demo',
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        s.add(u)
        await s.commit()
        print("--- RESET COMPLETE ---")
        print("Login Email: pranali@demo.com")
        print("Password: Pranali123!")

if __name__ == "__main__":
    asyncio.run(reset())
