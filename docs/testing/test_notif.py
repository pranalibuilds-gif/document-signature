import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.notifications.service import NotificationService
from app.common.enums import NotificationType
# Import all models to ensure registry is complete
from app.modules import models
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as s:
        ns = NotificationService(s)
        print("Sending test notification...")
        await ns.send_notification(
            recipient_email="test@example.com",
            subject="Manual Test",
            body="Hello world",
            type=NotificationType.INVITATION
        )

        print("Verifying in DB...")
        res = await s.execute(text("SELECT count(*) FROM notifications WHERE recipient_email = 'test@example.com'"))
        count = res.scalar()
        print(f"Notifications in DB: {count}")

if __name__ == "__main__":
    asyncio.run(run())
