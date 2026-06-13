import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.auth.models import EmailVerificationToken
from app.modules.users.models import User
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as s:
        # We need the RAW token, which isn't in the DB.
        # But wait, our register router prints the link to logs or returns it?
        # No, it just sends an email. I'll need to check the 'notifications' table.
        from app.modules.notifications.models import Notification
        r = await s.execute(select(Notification).where(Notification.recipient_email == 'test_user@example.com').order_by(Notification.created_at.desc()))
        notif = r.scalar_one_or_none()
        if notif:
            print(f"Body: {notif.body}")
        else:
            print("No notification found")

if __name__ == "__main__":
    asyncio.run(run())
