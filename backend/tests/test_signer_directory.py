import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.common.enums import DocumentStatus, SignerStatus, UserRole
from app.core.database import Base
from app.core.deps import get_current_user, get_db
from app.main import app
from app.modules.documents.models import Document
from app.modules.signers.models import DocumentSigner
from app.modules.users.models import User


@pytest.mark.asyncio
async def test_signer_directory_is_deduplicated_and_owner_scoped():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        owner = User(
            email=f"owner-{uuid.uuid4().hex}@example.com",
            hashed_password="unused",
            role=UserRole.USER,
        )
        other_owner = User(
            email=f"other-{uuid.uuid4().hex}@example.com",
            hashed_password="unused",
            role=UserRole.USER,
        )
        session.add_all([owner, other_owner])
        await session.flush()

        owner_documents = [
            Document(owner_id=owner.id, title="First", status=DocumentStatus.DRAFT),
            Document(owner_id=owner.id, title="Second", status=DocumentStatus.COMPLETED),
        ]
        other_document = Document(
            owner_id=other_owner.id,
            title="Private",
            status=DocumentStatus.DRAFT,
        )
        session.add_all([*owner_documents, other_document])
        await session.flush()

        session.add_all(
            [
                DocumentSigner(
                    document_id=owner_documents[0].id,
                    email="Alice@example.com",
                    status=SignerStatus.PENDING,
                ),
                DocumentSigner(
                    document_id=owner_documents[1].id,
                    email="alice@example.com",
                    status=SignerStatus.SIGNED,
                ),
                DocumentSigner(
                    document_id=other_document.id,
                    email="private@example.com",
                    status=SignerStatus.PENDING,
                ),
            ]
        )
        await session.commit()

        async def override_db():
            yield session

        async def override_user():
            return owner

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_user
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/signers/directory")
        finally:
            app.dependency_overrides.pop(get_db, None)
            app.dependency_overrides.pop(get_current_user, None)

    await engine.dispose()

    assert response.status_code == 200
    contacts = response.json()
    assert len(contacts) == 1
    assert contacts[0]["email"].lower() == "alice@example.com"
    assert contacts[0]["document_count"] == 2
    assert contacts[0]["last_used_at"]
