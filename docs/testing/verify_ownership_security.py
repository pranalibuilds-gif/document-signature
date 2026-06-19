import asyncio
import httpx
from app.modules.users.models import User
from app.modules.documents.models import Document
# Import models to ensure all SQLAlchemy relationships are initialized
from app.modules import models
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_ownership():
    async with AsyncSessionLocal() as session:
        # 1. Setup: Ensure we have the target user (User A)
        res = await session.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        user_a = res.scalar_one()

        # Identify a document belonging to User A
        res = await session.execute(select(Document).where(Document.owner_id == user_a.id).limit(1))
        doc_a = res.scalar_one()

        print(f"Target: Document '{doc_a.title}' ({doc_a.id}) owned by {user_a.email}")

    async with httpx.AsyncClient() as client:
        print("\n--- Phase 2: Ownership Boundary Audit ---")

        # 2. Create an "Attacker" User (Manager B)
        attacker_email = f"attacker_{uuid.uuid4().hex[:6]}@demo.com"
        reg_res = await client.post(f"{BASE_URL}/auth/register", json={
            "email": attacker_email,
            "password": "password123",
            "first_name": "Boundary",
            "last_name": "Tester"
        })

        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": attacker_email,
            "password": "password123"
        })
        attacker_token = login_res.json()["access_token"]
        print(f"Login successful for Attacker: {attacker_email}")

        # [TC-2.3.1] URL Tampering - Metadata Access
        print(f"\n[TC-2.3.1] Attacker attempting to access User A's document metadata...")
        attack_res = await client.get(
            f"{BASE_URL}/documents/{doc_a.id}",
            headers={"Authorization": f"Bearer {attacker_token}"}
        )
        print(f"RESULT: Status {attack_res.status_code}")
        if attack_res.status_code in [403, 404]:
            print("PASS: Access denied (Secured).")
        else:
            print(f"FAIL: Vulnerability! Attacker got status {attack_res.status_code}")

        # [TC-2.3.2] Final PDF Theft Attempt
        print(f"\n[TC-2.3.2] Attacker attempting to download User A's final PDF...")
        pdf_res = await client.get(
            f"{BASE_URL}/documents/{doc_a.id}/final-file",
            headers={"Authorization": f"Bearer {attacker_token}"}
        )
        print(f"RESULT: Status {pdf_res.status_code}")
        if pdf_res.status_code in [403, 404]:
            print("PASS: Download denied (Secured).")
        else:
            print(f"FAIL: Vulnerability! Attacker got status {pdf_res.status_code}")

        # [TC-2.3.3] Signer Enumeration Attempt
        print(f"\n[TC-2.3.3] Attacker attempting to list User A's signers...")
        signer_res = await client.get(
            f"{BASE_URL}/documents/{doc_a.id}/signers",
            headers={"Authorization": f"Bearer {attacker_token}"}
        )
        print(f"RESULT: Status {signer_res.status_code}")
        if signer_res.status_code in [403, 404]:
            print("PASS: Enumeration denied (Secured).")
        else:
            print(f"FAIL: Vulnerability! Attacker got status {signer_res.status_code}")

if __name__ == "__main__":
    asyncio.run(test_ownership())
