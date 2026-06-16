import asyncio
import os
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    doc_id = '3fa79030-76c4-49ca-85bb-0bcf90ed33a0'
    async with AsyncSessionLocal() as s:
        # 1. Check Document
        res = await s.execute(text("SELECT title, status FROM documents WHERE id = :id"), {"id": doc_id})
        doc = res.fetchone()
        if not doc:
            print(f"Document {doc_id} NOT FOUND in DB.")
            return
        print(f"Document Found: {doc.title} | Status: {doc.status}")

        # 2. Check DocumentFile
        res = await s.execute(text("SELECT file_name, file_path FROM document_files WHERE document_id = :id AND is_final = false"), {"id": doc_id})
        df = res.fetchone()
        if not df:
            print("No original DocumentFile record found.")
            return
        print(f"File Record Found: {df.file_name} | Path: {df.file_path}")

        # 3. Check Physical File
        if os.path.exists(df.file_path):
            print("PHYSICAL FILE EXISTS.")
        else:
            print(f"PHYSICAL FILE MISSING ON DISK at: {os.path.abspath(df.file_path)}")
            # List files in the storage/original directory to see what is there
            print("\nContents of storage/original:")
            if os.path.exists("storage/original"):
                for f in os.listdir("storage/original"):
                    print(f" - {f}")
            else:
                print("storage/original directory NOT FOUND.")

if __name__ == "__main__":
    asyncio.run(run())
