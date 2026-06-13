import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.notifications.models import Notification
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(Notification))
        notifs = r.scalars().all()
        print(f"Total notifications: {len(notifs)}")
        for n in notifs:
            print(f"Recipient: {n.recipient_email} | Body: {n.body if hasattr(n, 'body') else 'N/A'}")
            # Wait, Notification model might not have a 'body' column. Let me check the model.

if __name__ == "__main__":
    asyncio.run(run())
