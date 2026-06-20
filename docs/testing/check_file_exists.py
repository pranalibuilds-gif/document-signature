import asyncio
import os
import uuid
from app.core.database import AsyncSessionLocal
from app.modules.documents.models import Document, DocumentFile
from sqlalchemy import select

async def run():
    doc_id = uuid.UUID('3fa79030-76c4-49ca-85bb-0bcf90ed33a0')
    async with AsyncSessionLocal() as s:
        # 1. Check Document
        res = await s.execute(select(Document).where(Document.id == doc_id))
        doc = res.scalar_one_or_none()
        if not doc:
            print(f"Document {doc_id} NOT FOUND in DB.")
            return
        print(f"Document Found: {doc.title} | Status: {doc.status}")

        # 2. Check DocumentFile
        res = await s.execute(select(DocumentFile).where(DocumentFile.document_id == doc_id, not DocumentFile.is_final))
        df = res.scalar_one_or_none()
        if not df:
            print("No original DocumentFile record found.")
            return
        print(f"File Record Found: {df.file_name} | Path: {df.file_path}")

        # 3. Check Physical File
        # Path in DB is 'storage/original/...' but we are in 'backend/scripts' or 'backend'?
        # Usually it is relative to project root or backend root.
        # Let's check absolute path relative to current working directory.
        full_path = os.path.abspath(os.path.join(os.getcwd(), df.file_path))
        print(f"Checking absolute path: {full_path}")
        if os.path.exists(df.file_path):
            print("PHYSICAL FILE EXISTS.")
        else:
            print("PHYSICAL FILE MISSING ON DISK.")

if __name__ == "__main__":
    asyncio.run(run())
