import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.common.enums import DocumentStatus, FieldType, SignerStatus, UserRole
from app.core.database import Base
from app.core.deps import get_db
from app.main import app
from app.modules.documents.models import Document
from app.modules.fields.models import SignatureField
from app.modules.signers.models import DocumentSigner, SigningToken
from app.modules.signing.models import FieldValue


@pytest.mark.asyncio
async def test_signer_can_complete_assigned_fields_and_token_cannot_be_reused():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    raw_token = "one-time-signing-token"
    async with session_factory() as session:
        from app.modules.users.models import User

        owner = User(
            email=f"owner-{uuid.uuid4().hex}@example.com",
            hashed_password="unused",
            role=UserRole.USER,
            is_verified=True,
        )
        session.add(owner)
        await session.flush()

        document = Document(
            owner_id=owner.id,
            title="Signing workflow test",
            status=DocumentStatus.PENDING,
        )
        session.add(document)
        await session.flush()

        signer = DocumentSigner(
            document_id=document.id,
            email=f"signer-{uuid.uuid4().hex}@example.com",
            status=SignerStatus.PENDING,
        )
        remaining_signer = DocumentSigner(
            document_id=document.id,
            email=f"remaining-{uuid.uuid4().hex}@example.com",
            status=SignerStatus.PENDING,
        )
        session.add_all([signer, remaining_signer])
        await session.flush()

        field = SignatureField(
            document_id=document.id,
            assigned_signer_id=signer.id,
            page_number=1,
            x_coordinate=50,
            y_coordinate=80,
            width=20,
            height=5,
            field_type=FieldType.SIGNATURE,
            required=True,
        )
        token = SigningToken(
            document_signer_id=signer.id,
            token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
        session.add_all([field, token])
        await session.commit()

        async def override_db():
            yield session

        app.dependency_overrides[get_db] = override_db
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                session_response = await client.get(f"/api/v1/signing/{raw_token}")
                assert session_response.status_code == 200
                assert session_response.json()["signer"]["email"] == signer.email
                assert len(session_response.json()["fields"]) == 1

                submit_response = await client.post(
                    f"/api/v1/signing/{raw_token}/submit",
                    json={"values": [{"field_id": str(field.id), "value": "Signed Name"}]},
                )
                assert submit_response.status_code == 200

                replay_response = await client.post(
                    f"/api/v1/signing/{raw_token}/submit",
                    json={"values": [{"field_id": str(field.id), "value": "Signed Again"}]},
                )
        finally:
            app.dependency_overrides.pop(get_db, None)

        refreshed_signer = await session.get(DocumentSigner, signer.id)
        refreshed_document = await session.get(Document, document.id)
        field_values = (
            await session.execute(select(FieldValue).where(FieldValue.field_id == field.id))
        ).scalars().all()
        refreshed_token = await session.get(SigningToken, token.id)

    await engine.dispose()

    assert replay_response.status_code == 403
    assert refreshed_signer is not None
    assert refreshed_signer.status == SignerStatus.SIGNED
    assert refreshed_document is not None
    assert refreshed_document.status == DocumentStatus.PARTIALLY_SIGNED
    assert len(field_values) == 1
    assert field_values[0].value == "Signed Name"
    assert refreshed_token is not None
    assert refreshed_token.used_at is not None
