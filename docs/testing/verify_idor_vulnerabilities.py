import asyncio
import httpx
import uuid
from app.modules.users.models import User
from app.modules.documents.models import Document
# Relationship initialization
from app.modules import models
from app.core.database import AsyncSessionLocal
from sqlalchemy import select

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_idor():
    async with AsyncSessionLocal() as session:
        # Get target data (User A's data)
        res = await session.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        user_a = res.scalar_one()

        res = await session.execute(select(Document).where(Document.owner_id == user_a.id).limit(1))
        doc_a = res.scalar_one()

        target_doc_id = str(doc_a.id)
        print(f"Targeting Document: {target_doc_id}")

    async with httpx.AsyncClient() as client:
        print("\n--- Phase 2: IDOR Vulnerability Audit ---")

        # Create Attacker (User B)
        attacker_email = f"idor_attacker_{uuid.uuid4().hex[:6]}@demo.com"
        await client.post(f"{BASE_URL}/auth/register", json={
            "email": attacker_email,
            "password": "password123",
            "first_name": "IDOR",
            "last_name": "Tester"
        })
        login_res = await client.post(f"{BASE_URL}/auth/login", json={"email": attacker_email, "password": "password123"})
        token = login_res.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # IDOR Test Cases
        test_cases = [
            ("GET Document Metadata", f"/documents/{target_doc_id}"),
            ("GET Document Audit", f"/documents/{target_doc_id}/audit"),
            ("GET Document File", f"/documents/{target_doc_id}/file"),
            ("PATCH Update Document", f"/documents/{target_doc_id}"),
            ("DELETE Document", f"/documents/{target_doc_id}"),
            ("POST Activate Document", f"/documents/{target_doc_id}/activate"),
        ]

        for label, path in test_cases:
            print(f"\nChecking: {label}")
            method = label.split(' ')[0]
            if method == "GET":
                res = await client.get(f"{BASE_URL}{path}", headers=auth_header)
            elif method == "PATCH":
                res = await client.patch(f"{BASE_URL}{path}", headers=auth_header, json={"title": "IDOR Hacked"})
            elif method == "DELETE":
                res = await client.delete(f"{BASE_URL}{path}", headers=auth_header)
            elif method == "POST":
                res = await client.post(f"{BASE_URL}{path}", headers=auth_header)

            print(f"RESULT: Status {res.status_code}")
            if res.status_code in [403, 404]:
                print(f"PASS: Secured correctly.")
            elif res.status_code == 422:
                print(f"PASS: Validation error (Likely bad UUID/Format).")
            else:
                print(f"FAIL: VULNERABILITY! Unauthorized access allowed.")

if __name__ == "__main__":
    asyncio.run(test_idor())
