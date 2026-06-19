import asyncio
import httpx
import uuid
import hashlib
import secrets
import os
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.fields.models import SignatureField
from app.modules.notifications.models import Notification
from app.common.enums import DocumentStatus, SignerStatus, FieldType
from app.modules import models

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def get_token():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"{BASE_URL}/auth/login", json={
            "email": "pranali@northstar-tech.com",
            "password": "northstar2025"
        })
        return res.json()["access_token"], res.json()["refresh_token"]

async def run_chaos_audit():
    access_token, refresh_token = await get_token()
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        print("--- Phase 10: Data Corruption & Chaos Audit ---")

        # 1. [TC-10.1.1] Double Activation
        print("\n[TC-10.1.1] Double Activation Test")
        doc_res = await client.post(f"{BASE_URL}/documents", headers=headers, json={"title": "Double Activation Chaos"})
        doc_id = doc_res.json()["id"]

        # Setup doc for activation
        async with AsyncSessionLocal() as session:
            signer = DocumentSigner(id=uuid.uuid4(), document_id=uuid.UUID(doc_id), email="chaos@test.com")
            session.add(signer)
            field = SignatureField(id=uuid.uuid4(), document_id=uuid.UUID(doc_id), assigned_signer_id=signer.id, page_number=1, x_coordinate=10, y_coordinate=10, width=100, height=40, field_type=FieldType.SIGNATURE)
            session.add(field)
            # Add dummy file record with unique stored name
            stored_name = f"{uuid.uuid4()}.pdf"
            df = DocumentFile(document_id=uuid.UUID(doc_id), file_name="test.pdf", stored_name=stored_name, file_path=f"storage/original/{stored_name}", file_size=100, mime_type="application/pdf")
            session.add(df)
            await session.commit()

        # Call activate twice rapidly
        res1 = client.post(f"{BASE_URL}/documents/{doc_id}/activate", headers=headers)
        res2 = client.post(f"{BASE_URL}/documents/{doc_id}/activate", headers=headers)
        results = await asyncio.gather(res1, res2)
        print(f"Activation 1: {results[0].status_code}, Activation 2: {results[1].status_code}")

        async with AsyncSessionLocal() as session:
            count_tokens = await session.execute(select(func.count(SigningToken.id)).where(SigningToken.document_signer_id == signer.id))
            token_count = count_tokens.scalar()
            print(f"Signing Tokens for signer: {token_count}")
            if token_count == 1:
                print("PASS: Idempotent activation enforced.")
            else:
                print(f"FAIL: Duplicate tokens generated ({token_count})")

        # 2. [TC-10.5.1/2] Refresh Token Rotation
        print("\n[TC-10.5.1] Refresh Token Rotation Test")
        ref_res1 = await client.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
        print(f"First Refresh: {ref_res1.status_code}")
        if ref_res1.status_code == 200:
            new_refresh = ref_res1.json()["refresh_token"]
            print("PASS: New refresh token issued.")

            print("\n[TC-10.5.2] Reuse Old Refresh Token")
            ref_res2 = await client.post(f"{BASE_URL}/auth/refresh", json={"refresh_token": refresh_token})
            print(f"Old Token Reuse Result: {ref_res2.status_code}")
            if ref_res2.status_code in [401, 403]:
                print("PASS: Replay of old refresh token blocked.")
            else:
                print(f"FAIL: Old refresh token still valid!")
        else:
            print(f"FAIL: Refresh failed with {ref_res1.status_code}")

        # 3. [TC-10.6.2] Missing Final PDF File handling
        print("\n[TC-10.6.2] Missing Physical File Test")
        async with AsyncSessionLocal() as session:
            # Create a COMPLETED doc record pointing to a missing file
            comp_doc = Document(id=uuid.uuid4(), owner_id=(await session.execute(select(User.id).where(User.email == 'pranali@northstar-tech.com'))).scalar(), title="Missing File Test", status=DocumentStatus.COMPLETED)
            session.add(comp_doc)
            stored_name_missing = f"{uuid.uuid4()}.pdf"
            ff = DocumentFile(document_id=comp_doc.id, file_name="missing.pdf", stored_name=stored_name_missing, file_path=f"storage/final/{stored_name_missing}", file_size=100, mime_type="application/pdf", is_final=True)
            session.add(ff)
            await session.commit()
            comp_id = str(comp_doc.id)

        file_res = await client.get(f"{BASE_URL}/documents/{comp_id}/final-file", headers=headers)
        print(f"Download result for missing file: {file_res.status_code}")
        if file_res.status_code == 404:
            print("PASS: Missing file returned clean 404.")
        else:
            print(f"FAIL: Expected 404, got {file_res.status_code}")

if __name__ == "__main__":
    asyncio.run(run_chaos_audit())
