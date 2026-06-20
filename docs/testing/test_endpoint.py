import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.modules.documents.service import DocumentService
from app.modules.users.models import User
from sqlalchemy import select

async def run():
    doc_id = uuid.UUID('3fa79030-76c4-49ca-85bb-0bcf90ed33a0')
    async with AsyncSessionLocal() as s:
        # Get owner
        res = await s.execute(select(User).where(User.email == 'pranali@northstar-tech.com'))
        user = res.scalar_one()

        service = DocumentService(s)
        try:
            path = await service.get_document_file_path(doc_id, user.id)
            print(f"Success! Path: {path}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run())
