import asyncio
import httpx
import uuid
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.modules.notifications.models import Notification
from app.modules.documents.models import Document
from app.common.enums import NotificationType, DocumentStatus
from app.jobs.expiration_jobs import expire_documents_job
from datetime import datetime, timezone, timedelta
from app.modules import models

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_simulation():
    async with httpx.AsyncClient() as client:
        print("--- Phase 8: Email Flow Simulation ---")

        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # [TC-8.6.1] Expiration Notification Test
        print("\n[TC-8.6.1] Simulating Expiration flow...")
        doc_res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Expiration Flow Test"})
        exp_doc_id = doc_res.json()["id"]

        # Set to expired in DB
        async with AsyncSessionLocal() as session:
            await session.execute(update(Document).where(Document.id == uuid.UUID(exp_doc_id)).values(
                status=DocumentStatus.PENDING,
                expires_at=datetime.now(timezone.utc) - timedelta(days=1)
            ))
            await session.commit()
            print(f"Document {exp_doc_id} set to EXPIRED state in past.")

        # Trigger Job
        await expire_documents_job()

        async with AsyncSessionLocal() as session:
            # Check for EXPIRATION notification to OWNER
            res = await session.execute(select(Notification).where(
                Notification.document_id == uuid.UUID(exp_doc_id),
                Notification.recipient_email == "pranali@northstar-tech.com",
                Notification.type == NotificationType.EXPIRATION
            ))
            notifs = res.scalars().all()
            print(f"Expiration Notif count for owner: {len(notifs)}")
            if len(notifs) > 0:
                print(f"PASS: Owner notified of expiration.")
            else:
                print("FAIL: No expiration notification found for owner.")

if __name__ == "__main__":
    asyncio.run(run_simulation())
