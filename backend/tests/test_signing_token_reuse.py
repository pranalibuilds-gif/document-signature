from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.common.enums import DocumentStatus, SignerStatus
from app.modules.signing.service import SigningService


@pytest.mark.asyncio
async def test_validate_signing_token_rejects_already_used_tokens():
    service = SigningService(session=None)
    raw_token = "used-token"
    token = SimpleNamespace(
        document_signer_id="signer-1",
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        used_at=datetime.now(timezone.utc),
    )
    signer = SimpleNamespace(
        id="signer-1",
        email="alice@example.com",
        document_id="doc-1",
        status=SignerStatus.PENDING,
    )
    document = SimpleNamespace(id="doc-1", status=DocumentStatus.PENDING)

    service.signer_repo.get_token_by_hash = AsyncMock(return_value=token)
    service.signer_repo.get_by_id = AsyncMock(return_value=signer)
    service.doc_repo.get_by_id = AsyncMock(return_value=document)

    with pytest.raises(HTTPException) as exc_info:
        await service.validate_signing_token(raw_token)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "This signing link has already been used"
