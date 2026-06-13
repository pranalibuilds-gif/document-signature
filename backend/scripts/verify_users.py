import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(User))
        users = r.scalars().all()
        for u in users:
            print(f"User: {u.email} | ID: {u.id} | Verified: {u.is_verified} | Active: {u.is_active}")

if __name__ == "__main__":
    asyncio.run(run())
