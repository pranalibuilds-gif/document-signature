import asyncio
import httpx
import uuid
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.modules.notifications.models import Notification
from app.modules import models

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def run_scenario():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("--- Phase 12: Scenario B - Multi-Signer Rejection ---")

        login_res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup
        doc_res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Rejection Scenario Test"})
        doc_id = doc_res.json()["id"]
        with open("test_upload.pdf", "rb") as f:
            await client.post(f"{BASE_URL}/documents/{doc_id}/upload", headers=headers, files={"file": ("contract.pdf", f, "application/pdf")})

        # Add 2 Signers
        s_res1 = await client.post(f"{BASE_URL}/documents/{doc_id}/signers", headers=headers, json={"email": "signer1@test.com"})
        sid1 = s_res1.json()["id"]
        s_res2 = await client.post(f"{BASE_URL}/documents/{doc_id}/signers", headers=headers, json={"email": "signer2@test.com"})
        sid2 = s_res2.json()["id"]

        await client.post(f"{BASE_URL}/documents/{doc_id}/fields", headers=headers, json={
            "assigned_signer_id": sid1, "page_number": 1, "x_coordinate": 50, "y_coordinate": 50, "width": 100, "height": 40, "field_type": "SIGNATURE"
        })
        await client.post(f"{BASE_URL}/documents/{doc_id}/fields", headers=headers, json={
            "assigned_signer_id": sid2, "page_number": 1, "x_coordinate": 50, "y_coordinate": 150, "width": 100, "height": 40, "field_type": "SIGNATURE"
        })

        await client.post(f"{BASE_URL}/documents/{doc_id}/activate", headers=headers)

        # 1. Signer 1 Signs
        async with AsyncSessionLocal() as session:
            q = select(Notification.body).where(Notification.document_id == uuid.UUID(doc_id), Notification.recipient_email == "signer1@test.com")
            raw_token1 = (await session.execute(q)).scalar().split("/signing/")[1].split("/welcome")[0]

            q2 = select(Notification.body).where(Notification.document_id == uuid.UUID(doc_id), Notification.recipient_email == "signer2@test.com")
            raw_token2 = (await session.execute(q2)).scalar().split("/signing/")[1].split("/welcome")[0]

        print("Step 1: Signer 1 signs...")
        session_res = await client.get(f"{BASE_URL}/signing/{raw_token1}")
        fid1 = session_res.json()["fields"][0]["id"]
        await client.post(f"{BASE_URL}/signing/{raw_token1}/submit", json={"values": [{"field_id": fid1, "value": "S1 Signature"}]})

        # Check Status
        status_res = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        print(f"  Status after S1: {status_res.json()['status']}")

        # 2. Signer 2 Rejects
        print("Step 2: Signer 2 rejects...")
        await client.post(f"{BASE_URL}/signing/{raw_token2}/reject", json={"reason": "Incorrect terms in section 4."})

        # Verify Final Status
        final_res = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        print(f"  Final Document Status: {final_res.json()['status']}")

        if final_res.json()["status"] == "REJECTED":
            print("\nFINAL RESULT: PASS - Document rejected and workflow terminated.")
        else:
            print(f"\nFINAL RESULT: FAIL - Final status is {final_res.json()['status']}")

if __name__ == "__main__":
    asyncio.run(run_scenario())
