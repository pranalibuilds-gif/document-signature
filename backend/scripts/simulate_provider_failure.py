import asyncio
import httpx
import uuid
import secrets
import hashlib
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.notifications.models import Notification
from app.common.enums import NotificationStatus, DocumentStatus
from app.modules.documents.models import Document
from app.modules import models
from unittest.mock import patch

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_chaos_test():
    # We will use a mock to force the MailtrapProvider to fail
    # Since the server is running in a separate process, we can't easily patch it from here
    # UNLESS we trigger a flow that doesn't use the live server but uses the services directly.

    async with AsyncSessionLocal() as session:
        from app.modules.notifications.service import NotificationService
        from app.common.enums import NotificationType

        ns = NotificationService(session)

        print("--- Phase 9: Notification Failure Audit ---")

        # [TC-9.1.1] Email Provider Offline Simulation
        print("\n[TC-9.1.1] Simulating provider exception...")

        with patch.object(ns.provider, 'send_email', side_effect=Exception("Connection Timeout")):
            notif = await ns.send_notification(
                recipient_email="fail@test.com",
                subject="Chaos Test",
                body="Should fail but record should exist",
                type=NotificationType.INVITATION
            )

            print(f"Notification record created: {notif.id}")
            print(f"Status in record: {notif.status}")

            if notif.status == NotificationStatus.FAILED:
                print("PASS: Notification correctly marked as FAILED.")
            else:
                print(f"FAIL: Notification status is {notif.status}")

        # Verify Audit Log
        from app.modules.audit.models import AuditLog
        from app.common.enums import AuditEventType
        res = await session.execute(
            select(AuditLog).where(AuditLog.event_type == AuditEventType.NOTIFICATION_FAILED).limit(1)
        )
        audit = res.scalar_one_or_none()
        if audit:
            print(f"PASS: Audit log for failure created. Data: {audit.event_data}")
        else:
            print("FAIL: No audit log for notification failure found.")

        # [TC-9.3.1] Completion Resilience
        # We'll test if the DocumentService continues if notification fails.
        from app.modules.documents.service import DocumentService
        from app.modules.users.models import User

        doc_service = DocumentService(session)
        res = await session.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        user = res.scalar_one()

        doc = Document(id=uuid.uuid4(), owner_id=user.id, title="Resilience Test", status=DocumentStatus.PENDING)
        session.add(doc)
        await session.commit()

        print(f"\n[TC-9.3.1] Testing workflow resilience on email failure...")
        # Manually trigger a completion check where we know email will be attempted
        # We need signers for evaluate_document_status to do anything
        from app.modules.signers.models import DocumentSigner
        from app.common.enums import SignerStatus
        s1 = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="s1@res.com", status=SignerStatus.SIGNED)
        session.add(s1)
        await session.commit()

        with patch.object(doc_service.notification_service.provider, 'send_email', side_effect=Exception("SMTP Down")):
            # This should trigger evaluate -> completion -> email -> PDF gen
            # Even if email fails, it shouldn't crash
            try:
                await doc_service.evaluate_document_status(doc.id)
                print("PASS: evaluate_document_status finished without crashing despite email failure.")
            except Exception as e:
                print(f"FAIL: Workflow crashed on email failure: {e}")

            # Check if doc is COMPLETED
            await session.refresh(doc)
            print(f"Document status: {doc.status}")
            if doc.status == DocumentStatus.COMPLETED:
                print("PASS: Document reached COMPLETED state.")
            else:
                print(f"FAIL: Document stuck in {doc.status}")

if __name__ == "__main__":
    asyncio.run(run_chaos_test())
