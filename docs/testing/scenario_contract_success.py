import asyncio
import httpx
import uuid
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.notifications.models import Notification

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_scenario():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("--- Phase 12: Scenario A - Successful 3-Signer Contract ---")

        # 1. Login
        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create and Upload
        doc_res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "End-to-End Success Scenario"})
        doc_id = doc_res.json()["id"]
        with open("test_upload.pdf", "rb") as f:
            await client.post(f"{BASE_URL}/documents/{doc_id}/upload", headers=headers, files={"file": ("contract.pdf", f, "application/pdf")})

        # 3. Add Signers A, B, C
        signers = ["signer_a@test.com", "signer_b@test.com", "signer_c@test.com"]
        signer_ids = []
        for email in signers:
            s_res = await client.post(f"{BASE_URL}/documents/{doc_id}/signers", headers=headers, json={"email": email})
            signer_ids.append(s_res.json()["id"])

        # 4. Place Fields
        for sid in signer_ids:
            await client.post(f"{BASE_URL}/documents/{doc_id}/fields", headers=headers, json={
                "assigned_signer_id": sid, "page_number": 1, "x_coordinate": 50, "y_coordinate": 50, "width": 100, "height": 40, "field_type": "SIGNATURE"
            })

        # 5. Activate
        print("Step 5: Activating Document...")
        await client.post(f"{BASE_URL}/documents/{doc_id}/activate", headers=headers)

        # 6. Capture Tokens
        tokens = []
        async with AsyncSessionLocal() as session:
            q = select(Notification.recipient_email, Notification.body).where(Notification.document_id == uuid.UUID(doc_id))
            res = await session.execute(q)
            for email, body in res.all():
                raw_token = body.split("/signing/")[1].split("/welcome")[0]
                tokens.append((email, raw_token))

        # 7. Sign in sequence
        for i, (email, raw_token) in enumerate(tokens):
            print(f"Step {7+i}: Signer {email} is signing...")
            # Fetch field ID
            session_res = await client.get(f"{BASE_URL}/signing/{raw_token}")
            fid = session_res.json()["fields"][0]["id"]

            await client.post(f"{BASE_URL}/signing/{raw_token}/submit", json={
                "values": [{"field_id": fid, "value": f"Sig of {email}"}]
            })

            # Check Document Status after each sign
            status_res = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
            current_status = status_res.json()["status"]
            print(f"  Document Status: {current_status}")

        # 8. Verify Completion
        final_res = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        if final_res.json()["status"] == "COMPLETED":
            print("\nFINAL RESULT: PASS - Document reached COMPLETED state successfully.")
        else:
            print(f"\nFINAL RESULT: FAIL - Final status is {final_res.json()['status']}")

if __name__ == "__main__":
    asyncio.run(run_scenario())
