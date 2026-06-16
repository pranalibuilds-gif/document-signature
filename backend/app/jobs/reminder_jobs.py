from datetime import datetime, timezone
from app.core.database import AsyncSessionLocal
from app.modules.signers.repository import SignerRepository
from app.modules.notifications.service import NotificationService
from app.modules.documents.repository import DocumentRepository
from app.common.enums import NotificationType
from app.core.logging import logger

async def send_signer_reminders_job():
    logger.info("Starting signer reminder job...")
    async with AsyncSessionLocal() as session:
        try:
            signer_repo = SignerRepository(session)
            notification_service = NotificationService(session)
            doc_repo = DocumentRepository(session)

            # Send reminders for people who haven't signed after 3 days
            pending_signers = await signer_repo.get_pending_reminders(days=3)

            for signer in pending_signers:
                document = await doc_repo.get_by_id(signer.document_id)
                if not document:
                    continue

                # Fetch the raw token from Notification or Audit logs if possible,
                # but SigningToken only stores hash.
                # For this demo/simulation, we'll assume we send a generic secure link
                # that requires a fresh token generation or uses the email context.
                # In a real app, we'd store the invitation_token_id or similar.

                # For now, let's just make sure the email is triggered correctly.
                link = f"http://localhost:3000/signing/remind/{signer.id}"

                await notification_service.send_notification(
                    recipient_email=signer.email,
                    subject=f"Reminder: Signature Required - {document.title}",
                    body=f"This is a reminder to sign '{document.title}'. You can access your signing session here: {link}",
                    type=NotificationType.REMINDER,
                    document_id=signer.document_id
                )

                signer.last_reminder_sent_at = datetime.now(timezone.utc)

            await session.commit()
            logger.info(f"Reminder job finished. Processed {len(pending_signers)} signers.")

        except Exception as e:
            logger.error(f"Error in send_signer_reminders_job: {e}")
            await session.rollback()
