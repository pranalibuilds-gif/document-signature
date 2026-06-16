import asyncio
import httpx
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.modules.documents.models import Document
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.fields.models import SignatureField
from app.common.enums import DocumentStatus, SignerStatus, FieldType
from sqlalchemy import select

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def setup_test_data():
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        owner = res.scalar_one()

        doc = Document(id=uuid.uuid4(), owner_id=owner.id, title="Abuse Test Doc", status=DocumentStatus.PENDING)
        session.add(doc)

        signer_a = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="signer_a@test.com", status=SignerStatus.PENDING)
        signer_b = DocumentSigner(id=uuid.uuid4(), document_id=doc.id, email="signer_b@test.com", status=SignerStatus.PENDING)
        session.add(signer_a)
        session.add(signer_b)

        field_a = SignatureField(id=uuid.uuid4(), document_id=doc.id, assigned_signer_id=signer_a.id, page_number=1, x_coordinate=10, y_coordinate=10, width=100, height=40, field_type=FieldType.SIGNATURE)
        field_b = SignatureField(id=uuid.uuid4(), document_id=doc.id, assigned_signer_id=signer_b.id, page_number=1, x_coordinate=20, y_coordinate=20, width=100, height=40, field_type=FieldType.SIGNATURE)
        session.add(field_a)
        session.add(field_b)

        # Create valid tokens
        raw_a = secrets.token_urlsafe(32)
        raw_b = secrets.token_urlsafe(32)

        token_a = SigningToken(document_signer_id=signer_a.id, token_hash=hashlib.sha256(raw_a.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(days=1))
        token_b = SigningToken(document_signer_id=signer_b.id, token_hash=hashlib.sha256(raw_b.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(days=1))
        session.add(token_a)
        session.add(token_b)

        # Create an expired token
        raw_expired = secrets.token_urlsafe(32)
        token_expired = SigningToken(document_signer_id=signer_a.id, token_hash=hashlib.sha256(raw_expired.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
        session.add(token_expired)

        await session.commit()
        return {
            "doc_id": doc.id,
            "signer_a_id": signer_a.id,
            "signer_b_id": signer_b.id,
            "field_a_id": field_a.id,
            "field_b_id": field_b.id,
            "token_a": raw_a,
            "token_b": raw_b,
            "token_expired": raw_expired
        }

async def run_abuse_tests():
    data = await setup_test_data()
    async with httpx.AsyncClient() as client:
        print("--- Phase 4: Signing Token Abuse Audit ---")

        # TC-4.1.1 Random Token
        print("\n[TC-4.1.1] Random Token Test")
        res = await client.get(f"{BASE_URL}/signing/not-a-token")
        print(f"Result: {res.status_code}")
        if res.status_code == 404: print("PASS")
        else: print(f"FAIL: Got {res.status_code}")

        # TC-4.1.2 Modified Token
        print("\n[TC-4.1.2] Modified Token Test")
        modified = data['token_a'][:-1] + ('z' if data['token_a'][-1] != 'z' else 'y')
        res = await client.get(f"{BASE_URL}/signing/{modified}")
        print(f"Result: {res.status_code}")
        if res.status_code == 404: print("PASS")
        else: print(f"FAIL: Got {res.status_code}")

        # TC-4.2.1 Expired Link
        print("\n[TC-4.2.1] Expired Token Test")
        res = await client.get(f"{BASE_URL}/signing/{data['token_expired']}")
        print(f"Result: {res.status_code}")
        if res.status_code == 410: print("PASS")
        else: print(f"FAIL: Got {res.status_code}")

        # TC-4.4.1 Assigned Fields Only
        print("\n[TC-4.4.1] Field Scope Test (Signer A)")
        res = await client.get(f"{BASE_URL}/signing/{data['token_a']}")
        body = res.json()
        fields = body.get('fields', [])
        field_ids = [f['id'] for f in fields]
        print(f"Visible fields: {len(fields)}")
        if len(fields) == 1 and str(data['field_a_id']) in field_ids:
            print("PASS: Only Signer A fields returned.")
        else:
            print(f"FAIL: Incorrect fields returned. IDs: {field_ids}")

        # TC-4.4.2 Cross-Signer Completion
        print("\n[TC-4.4.2] Cross-Signer Field Submission Test")
        res = await client.post(f"{BASE_URL}/signing/{data['token_a']}/submit", json={
            "values": [{"field_id": str(data['field_b_id']), "value": "Hacked"}]
        })
        print(f"Result: {res.status_code}")
        if res.status_code in [400, 403]: print("PASS: Cross-signer submission blocked.")
        else: print(f"FAIL: Vulnerability! Signer A could sign Signer B's field. Status: {res.status_code}")

        # TC-4.3.1 Double Submit
        print("\n[TC-4.3.1] Double Submit Test (Signer A)")
        # First valid submit
        res1 = await client.post(f"{BASE_URL}/signing/{data['token_a']}/submit", json={
            "values": [{"field_id": str(data['field_a_id']), "value": "Valid Sig"}]
        })
        print(f"First submit: {res1.status_code}")
        # Second submit
        res2 = await client.post(f"{BASE_URL}/signing/{data['token_a']}/submit", json={
            "values": [{"field_id": str(data['field_a_id']), "value": "Repeat Sig"}]
        })
        print(f"Second submit: {res2.status_code}")
        if res2.status_code == 403: print("PASS: Replay blocked.")
        else: print(f"FAIL: Replay allowed. Status: {res2.status_code}")

        # TC-4.6.2 Reject Then Sign
        print("\n[TC-4.6.2] Reject then Sign Test (Signer B)")
        rej_res = await client.post(f"{BASE_URL}/signing/{data['token_b']}/reject", json={"reason": "Changing my mind"})
        print(f"Rejection: {rej_res.status_code}")
        sign_res = await client.post(f"{BASE_URL}/signing/{data['token_b']}/submit", json={
            "values": [{"field_id": str(data['field_b_id']), "value": "Regret Sign"}]
        })
        print(f"Sign attempt after rejection: {sign_res.status_code}")
        if sign_res.status_code == 403: print("PASS: Finalized state enforced.")
        else: print(f"FAIL: Signed after rejection! Status: {sign_res.status_code}")

if __name__ == "__main__":
    asyncio.run(run_abuse_tests())
