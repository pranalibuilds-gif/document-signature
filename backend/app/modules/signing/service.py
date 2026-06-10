import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.signing.models import FieldValue
from app.modules.signing.repository import SigningRepository
from app.modules.signing.schemas import SigningSubmission, RejectionRequest
from app.modules.signers.repository import SignerRepository
from app.modules.signers.models import SigningToken, DocumentSigner
from app.modules.documents.service import DocumentService
from app.modules.documents.repository import DocumentRepository
from app.modules.fields.repository import SignatureFieldRepository
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, SignerStatus, AuditActorType, AuditEventType, FieldType
from app.core.logging import logger

class SigningService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SigningRepository(session)
        self.signer_repo = SignerRepository(session)
        self.doc_repo = DocumentRepository(session)
        self.field_repo = SignatureFieldRepository(session)
        self.audit_service = AuditService(session)
        self.doc_service = DocumentService(session)

    def _hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    async def validate_signing_token(self, raw_token: str) -> SigningToken:
        token_hash = self._hash_token(raw_token)
        token = await self.signer_repo.get_token_by_hash(token_hash)

        if not token:
            logger.warning(f"Invalid signing link attempt with hash: {token_hash}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid signing link")

        if token.expires_at < datetime.now(timezone.utc):
            logger.warning(f"Expired signing link attempt for signer: {token.document_signer_id}")
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="Signing link has expired")

        # used_at logic: In 3.4B we don't block opening if used_at is set,
        # but we might block if the signer has already signed.

        signer = await self.signer_repo.get_by_id(token.document_signer_id)
        logger.info(f"Signer session opened: {signer.email} for document {signer.document_id}")

        if signer.status == SignerStatus.SIGNED:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You have already signed this document")

        document = await self.doc_repo.get_by_id(signer.document_id)
        if document.status in [DocumentStatus.COMPLETED, DocumentStatus.REJECTED, DocumentStatus.CANCELED, DocumentStatus.EXPIRED]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Document is {document.status}")

        return token

    async def get_signer_document(self, raw_token: str) -> Dict[str, Any]:
        token = await self.validate_signing_token(raw_token)
        signer = await self.signer_repo.get_by_id(token.document_signer_id)
        document = await self.doc_repo.get_by_id(signer.document_id)
        fields = await self.field_repo.list_by_signer(signer.id)

        return {
            "document": document,
            "signer": signer,
            "fields": fields
        }

    async def submit_signature(self, raw_token: str, submission: SigningSubmission) -> None:
        token = await self.validate_signing_token(raw_token)
        signer = await self.signer_repo.get_by_id(token.document_signer_id)
        document = await self.doc_repo.get_by_id(signer.document_id)

        assigned_fields = await self.field_repo.list_by_signer(signer.id)
        assigned_field_ids = {f.id for f in assigned_fields}
        required_field_ids = {f.id for f in assigned_fields if f.required}

        submitted_values = {v.field_id: v.value for v in submission.values}

        # 1. Validation: All submitted fields must belong to signer
        for field_id in submitted_values:
            if field_id not in assigned_field_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Field does not belong to you")

        # 2. Validation: All required fields must be present
        for req_id in required_field_ids:
            if req_id not in submitted_values or not submitted_values[req_id].strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Required fields are missing")

        # 3. Value-specific validation (Basic)
        for field in assigned_fields:
            val = submitted_values.get(field.id)
            if not val: continue

            if field.field_type == FieldType.DATE:
                try:
                    datetime.fromisoformat(val)
                except ValueError:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date format for field {field.id}")

        # 4. Persistence (Single Transaction - assuming caller commits)
        now = datetime.now(timezone.utc)
        for field_id, value in submitted_values.items():
            field_val = FieldValue(
                field_id=field_id,
                document_signer_id=signer.id,
                value=value,
                completed_at=now
            )
            await self.repo.create_field_value(field_val)

            # Audit field completion
            field = next(f for f in assigned_fields if f.id == field_id)
            await self.audit_service.record_event(
                event_type=AuditEventType.FIELD_COMPLETED,
                actor_type=AuditActorType.USER,
                user_id=signer.user_id, # Might be NULL
                document_id=document.id,
                event_data={"field_type": field.field_type}
            )

        # 5. Update Signer
        signer.status = SignerStatus.SIGNED
        signer.signed_at = now
        # used_at updated here as approved
        token.used_at = now

        # 6. Audit Document Signed
        await self.audit_service.record_event(
            event_type=AuditEventType.DOCUMENT_SIGNED,
            actor_type=AuditActorType.USER,
            user_id=signer.user_id,
            document_id=document.id,
            event_data={"signer_email": signer.email}
        )

        # 7. Evaluate Document Status
        await self.doc_service.evaluate_document_status(document.id)
        logger.info(f"Signer {signer.email} completed signing for document {document.id}")

    async def reject_document(self, raw_token: str, rejection: RejectionRequest) -> None:
        token = await self.validate_signing_token(raw_token)
        signer = await self.signer_repo.get_by_id(token.document_signer_id)
        document = await self.doc_repo.get_by_id(signer.document_id)

        # 1. Update Signer
        now = datetime.now(timezone.utc)
        signer.status = SignerStatus.REJECTED
        signer.rejected_at = now
        signer.rejection_reason = rejection.reason
        token.used_at = now

        # 2. Evaluate Document Status (This will mark document as REJECTED and notify owner)
        await self.doc_service.evaluate_document_status(document.id)
        logger.info(f"Signer {signer.email} rejected document {document.id}")
