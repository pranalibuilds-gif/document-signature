import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.notifications.service import NotificationService
from app.common.enums import NotificationType, NotificationStatus
from app.modules import models
from unittest.mock import patch
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as s:
        ns = NotificationService(s)

        print("--- Phase 9: Notification Retry Audit ---")

        # 1. Create a FAILED notification manually
        print("\n[Setup] Forcing a failure...")
        with patch.object(ns.provider, 'send_email', side_effect=Exception("Manual Failure")):
            await ns.send_notification(
                recipient_email="retry@test.com",
                subject="Retry Test",
                body="Redeliver me",
                type=NotificationType.INVITATION
            )

        # 2. Trigger Retry (with SUCCESS provider)
        print("\n[TC-9.1.2] Triggering Bulk Retry...")
        # No patch here means provider returns True by default
        count = await ns.retry_failed_notifications()
        print(f"Success count: {count}")

        # 3. Verify in DB
        res = await s.execute(text("SELECT status FROM notifications WHERE recipient_email = 'retry@test.com'"))
        status = res.scalar()
        print(f"Final status in DB: {status}")

        if status == NotificationStatus.SENT:
            print("PASS: Notification successfully retried and delivered.")
        else:
            print(f"FAIL: Expected SENT, got {status}")

if __name__ == "__main__":
    asyncio.run(run())
