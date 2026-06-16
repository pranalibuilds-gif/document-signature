import asyncio
import httpx
import uuid
import hashlib
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.documents.models import Document
from app.modules.fields.models import SignatureField
from app.common.enums import DocumentStatus, SignerStatus, FieldType
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_signer_isolation():
    raw_token = ""
    doc_id = None

    async with AsyncSessionLocal() as session:
        # 1. Setup: Create a fresh test document
        from app.modules.users.models import User
        res = await session.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        owner = res.scalar_one()

        doc = Document(id=uuid.uuid4(), owner_id=owner.id, title="Signer Isolation Test", status=DocumentStatus.PENDING)
        session.add(doc)

        signer = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="signer@isolation.com", status=SignerStatus.PENDING)
        session.add(signer)

        field = SignatureField(
            id=uuid.uuid4(),
            document_id=doc.id,
            assigned_signer_id=signer.id,
            page_number=1,
            x_coordinate=10,
            y_coordinate=10,
            width=100,
            height=40,
            field_type=FieldType.SIGNATURE
        )
        session.add(field)

        raw_token = "isolation_test_token_" + uuid.uuid4().hex
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        db_token = SigningToken(document_signer_id=signer.id, token_hash=token_hash, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
        session.add(db_token)

        await session.commit()
        doc_id = doc.id
        field_id = field.id
        print(f"Test Document created: {doc_id} with token: {raw_token}")

    async with httpx.AsyncClient() as client:
        print("\n--- Phase 2: Signer Isolation Audit ---")

        # [TC-2.4.3] Token Reuse: Step 1 - Submit successfully
        print(f"\n[TC-2.4.3] Signer submitting signature for the first time...")
        submit_res = await client.post(f"{BASE_URL}/signing/{raw_token}/submit", json={
            "values": [{"field_id": str(field_id), "value": "Isolation Test Signature"}]
        })
        print(f"RESULT: Status {submit_res.status_code}")
        if submit_res.status_code == 200:
            print("PASS: First submission successful.")
        else:
            print(f"FAIL: First submission failed with {submit_res.status_code}: {submit_res.text}")
            return

        # [TC-2.4.3] Token Reuse: Step 2 - Submit AGAIN
        print(f"\n[TC-2.4.3] Attempting to reuse the same signing token...")
        reuse_res = await client.post(f"{BASE_URL}/signing/{raw_token}/submit", json={
            "values": [{"field_id": str(field_id), "value": "Malicious Reuse"}]
        })
        print(f"RESULT: Status {reuse_res.status_code}")
        if reuse_res.status_code in [403, 410, 401]:
            print(f"PASS: Token reuse blocked correctly ({reuse_res.status_code}).")
            msg = reuse_res.json().get('detail', '')
            print(f"Message: {msg}")
        else:
            print(f"FAIL: Vulnerability! Token reused successfully. Status: {reuse_res.status_code}")

if __name__ == "__main__":
    asyncio.run(test_signer_isolation())
