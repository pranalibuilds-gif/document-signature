import asyncio
import httpx
import uuid
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.fields.models import SignatureField
from app.common.enums import DocumentStatus, SignerStatus, FieldType
from sqlalchemy import select

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_owner_token():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        return res.json()["access_token"]

async def run_workflow_stress_tests():
    token = await get_owner_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        print("--- Phase 5: Document Lifecycle Stress Audit ---")

        # 1. [TC-5.1.1] Empty Activation attempt
        print("\n[TC-5.1.1] Empty Activation Test")
        doc_res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Empty Activation Test"})
        doc_id = doc_res.json()["id"]
        act_res = await client.post(f"{BASE_URL}/documents/{doc_id}/activate", headers=headers)
        print(f"Result: {act_res.status_code}")
        if act_res.status_code in [400, 422]: print("PASS: Blocked empty activation.")
        else: print(f"FAIL: Activation status: {act_res.status_code}")

        # 2. [TC-5.2.1] Edit Locked Document (Pending)
        print("\n[TC-5.2.1] Edit Locked Document Test")
        # Find a PENDING document
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Document).where(Document.status == DocumentStatus.PENDING).limit(1))
            pending_doc = res.scalar_one()
            pending_id = str(pending_doc.id)

        # Try to update title
        edit_res = await client.patch(f"{BASE_URL}/documents/{pending_id}", headers=headers, json={"title": "Hacked Title"})
        print(f"Edit Title Result: {edit_res.status_code}")

        # Try to upload new PDF
        with open("test_upload.pdf", "rb") as f:
            files = {"file": ("new.pdf", f, "application/pdf")}
            upload_res = await client.post(f"{BASE_URL}/documents/{pending_id}/upload", headers=headers, files=files)
        print(f"Upload PDF Result: {upload_res.status_code}")

        if edit_res.status_code == 403 and upload_res.status_code == 409:
            print("PASS: Pending document is immutable.")
        else:
            print(f"FAIL: Vulnerability! Edit: {edit_res.status_code}, Upload: {upload_res.status_code}")

        # 3. [TC-5.5.2] Midway Rejection
        print("\n[TC-5.5.2] Midway Rejection Test")
        async with AsyncSessionLocal() as session:
            # Setup 2-signer doc
            doc = Document(id=uuid.uuid4(), owner_id=pending_doc.owner_id, title="Midway Rejection Test", status=DocumentStatus.PENDING)
            s1 = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="s1@test.com", status=SignerStatus.SIGNED)
            s2 = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="s2@test.com", status=SignerStatus.PENDING)
            session.add_all([doc, s1, s2])

            raw_t2 = secrets.token_urlsafe(32)
            t2 = SigningToken(document_signer_id=s2.id, token_hash=hashlib.sha256(raw_t2.encode()).hexdigest(), expires_at=datetime.now(timezone.utc)+timedelta(days=1))
            session.add(t2)
            await session.commit()
            mid_id = str(doc.id)

        # Signer 2 Rejects
        rej_res = await client.post(f"{BASE_URL}/signing/{raw_t2}/reject", json={"reason": "Business conflict"})
        print(f"Rejection result: {rej_res.status_code}")

        # Verify Document Status
        check_res = await client.get(f"{BASE_URL}/documents/{mid_id}", headers=headers)
        new_status = check_res.json()["status"]
        print(f"New Document Status: {new_status}")
        if new_status == "REJECTED":
            print("PASS: Document rejected immediately.")
        else:
            print(f"FAIL: Expected REJECTED, got {new_status}")

        # 4. [TC-5.7.1] Single Generation check (Simulate Race)
        print("\n[TC-5.7.1] Idempotent Completion Test")
        async with AsyncSessionLocal() as session:
            # Find a COMPLETED document
            res = await session.execute(select(Document).where(Document.status == DocumentStatus.COMPLETED).limit(1))
            comp_doc = res.scalar_one()

            # Count files
            res = await session.execute(select(DocumentFile).where(DocumentFile.document_id == comp_doc.id, DocumentFile.is_final == True))
            files = res.scalars().all()
            print(f"Completed Doc {comp_doc.id} has {len(files)} final PDF(s).")
            if len(files) == 1:
                print("PASS: Single final PDF generated.")
            else:
                print(f"FAIL: Multiple final PDFs detected ({len(files)}).")

if __name__ == "__main__":
    asyncio.run(run_workflow_stress_tests())
