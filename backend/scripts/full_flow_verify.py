import asyncio
import uuid
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.modules.documents.models import Document, DocumentFile
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.fields.models import SignatureField
from app.common.enums import DocumentStatus, SignerStatus, FieldType
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as s:
        # 1. Get verified user
        res = await s.execute(select(User).where(User.email == 'pranali@demo.com'))
        user = res.scalar_one()

        # 2. Create document
        doc = Document(
            id=uuid.uuid4(),
            owner_id=user.id,
            title="RC FULL VERIFIED FLOW",
            status=DocumentStatus.DRAFT
        )
        s.add(doc)

        # 3. Create file record
        stored_name = f"{uuid.uuid4()}.pdf"
        file = DocumentFile(
            id=uuid.uuid4(),
            document_id=doc.id,
            file_name="verified.pdf",
            stored_name=stored_name,
            file_path=f"storage/original/{stored_name}",
            file_size=1024,
            mime_type="application/pdf",
            is_final=False
        )
        s.add(file)

        # 4. Create signer
        signer = DocumentSigner(
            id=uuid.uuid4(),
            document_id=doc.id,
            email="rc_signer_final@example.com",
            status=SignerStatus.PENDING
        )
        s.add(signer)

        # 5. Create field
        field = SignatureField(
            id=uuid.uuid4(),
            document_id=doc.id,
            assigned_signer_id=signer.id,
            field_type=FieldType.SIGNATURE,
            page_number=1,
            x_coordinate=50,
            y_coordinate=50,
            width=150,
            height=50,
            required=True
        )
        s.add(field)
        await s.flush()

        # 6. Activate
        doc.status = DocumentStatus.PENDING
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        db_token = SigningToken(
            id=uuid.uuid4(),
            document_signer_id=signer.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30)
        )
        s.add(db_token)
        await s.commit()

        print(f"DOC_ID:{doc.id}")
        print(f"RAW_TOKEN:{raw_token}")
        print(f"FIELD_ID:{field.id}")

if __name__ == "__main__":
    asyncio.run(run())
