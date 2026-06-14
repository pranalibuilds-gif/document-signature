import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.documents.models import Document
from app.modules.signers.models import DocumentSigner
# This import is CRUCIAL for SQLAlchemy to map relationships in standalone scripts
from app.modules import models
from sqlalchemy import select, func

async def audit():
    async with AsyncSessionLocal() as s:
        # 1. Document Titles & Statuses
        r = await s.execute(select(Document.title, Document.status).limit(10))
        docs = r.all()
        print("--- Document Sample ---")
        for title, status in docs:
            print(f"Title: {title} | Status: {status}")

        # 2. Status Distribution
        r = await s.execute(select(Document.status, func.count(Document.id)).group_by(Document.status))
        dist = r.all()
        print("\n--- Status Distribution ---")
        for status, count in dist:
            print(f"{status}: {count}")

        # 3. Signer Emails (Check consistency)
        r = await s.execute(select(DocumentSigner.email).distinct().limit(10))
        emails = r.scalars().all()
        print("\n--- Signer Emails (Sample) ---")
        for email in emails:
            print(f"Email: {email}")

if __name__ == "__main__":
    asyncio.run(audit())
