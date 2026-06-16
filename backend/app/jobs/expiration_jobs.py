from app.core.database import AsyncSessionLocal
from app.modules.documents.repository import DocumentRepository
from app.modules.audit.service import AuditService
from app.modules.notifications.service import NotificationService
from app.common.enums import DocumentStatus, AuditActorType, AuditEventType, NotificationType
from app.modules.users.repository import UserRepository
from app.core.logging import logger

async def expire_documents_job():
    logger.info("Starting document expiration job...")
    async with AsyncSessionLocal() as session:
        try:
            doc_repo = DocumentRepository(session)
            audit_service = AuditService(session)
            notification_service = NotificationService(session)
            user_repo = UserRepository(session)

            expired_docs = await doc_repo.get_expired_documents()

            for doc in expired_docs:
                doc.status = DocumentStatus.EXPIRED
                await doc_repo.update(doc)

                await audit_service.record_event(
                    event_type=AuditEventType.LINK_EXPIRED,
                    actor_type=AuditActorType.SYSTEM,
                    document_id=doc.id
                )

                # TC-8.6.1: Notify Owner about expiration
                owner = await user_repo.get_by_id(doc.owner_id)
                if owner:
                    await notification_service.send_notification(
                        recipient_email=owner.email,
                        subject=f"Document Expired: {doc.title}",
                        body=f"Your document '{doc.title}' has expired without being fully signed.",
                        type=NotificationType.EXPIRATION,
                        document_id=doc.id
                    )

                logger.info(f"Document {doc.id} marked as EXPIRED and owner notified.")

            await session.commit()
            logger.info(f"Expiration job finished. Processed {len(expired_docs)} documents.")

        except Exception as e:
            logger.error(f"Error in expire_documents_job: {e}")
            await session.rollback()
