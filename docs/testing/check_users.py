import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(User.email))
        emails = r.scalars().all()
        print(f"Emails: {emails}")

if __name__ == "__main__":
    asyncio.run(check())
