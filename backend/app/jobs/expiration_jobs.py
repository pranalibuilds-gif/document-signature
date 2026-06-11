from app.core.database import AsyncSessionLocal
from app.modules.documents.repository import DocumentRepository
from app.modules.audit.service import AuditService
from app.common.enums import DocumentStatus, AuditActorType, AuditEventType
from app.core.logging import logger

async def expire_documents_job():
    logger.info("Starting document expiration job...")
    async with AsyncSessionLocal() as session:
        try:
            doc_repo = DocumentRepository(session)
            audit_service = AuditService(session)

            expired_docs = await doc_repo.get_expired_documents()

            for doc in expired_docs:
                doc.status = DocumentStatus.EXPIRED
                await doc_repo.update(doc)

                await audit_service.record_event(
                    event_type=AuditEventType.LINK_EXPIRED, # Reusing for doc expiration
                    actor_type=AuditActorType.SYSTEM,
                    document_id=doc.id
                )
                logger.info(f"Document {doc.id} marked as EXPIRED.")

            await session.commit()
            logger.info(f"Expiration job finished. Processed {len(expired_docs)} documents.")

        except Exception as e:
            logger.error(f"Error in expire_documents_job: {e}")
            await session.rollback()
