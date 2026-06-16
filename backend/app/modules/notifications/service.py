import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.providers.mailtrap import MailtrapProvider
from app.modules.audit.service import AuditService
from app.common.enums import NotificationType, NotificationStatus, AuditActorType, AuditEventType
from app.core.logging import logger

class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NotificationRepository(session)
        self.audit_service = AuditService(session)
        self.provider = MailtrapProvider()

    async def send_notification(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        type: NotificationType,
        user_id: uuid.UUID | None = None,
        document_id: uuid.UUID | None = None,
    ) -> Notification:
        # 1. Create record
        notification = Notification(
            user_id=user_id,
            document_id=document_id,
            type=type,
            recipient_email=recipient_email,
            subject=subject,
            body=body,
            status=NotificationStatus.PENDING
        )
        notification = await self.repo.create(notification)

        # 2. Attempt delivery
        success = False
        error_msg = None
        try:
            success = await self.provider.send_email(recipient_email, subject, body)
        except Exception as e:
            error_msg = str(e)

        # 3. Update status
        if success:
            await self.repo.update_status(notification.id, NotificationStatus.SENT)
            logger.info(f"Notification sent: {notification.id} to {recipient_email}")

            # Audit success
            await self.audit_service.record_event(
                event_type=AuditEventType.NOTIFICATION_SENT,
                actor_type=AuditActorType.SYSTEM,
                user_id=user_id,
                document_id=document_id,
                event_data={"type": type, "recipient": recipient_email}
            )
        else:
            final_error = error_msg or "Provider delivery failed"
            await self.repo.update_status(notification.id, NotificationStatus.FAILED, final_error)
            logger.error(f"Notification failed: {notification.id} to {recipient_email}. Error: {final_error}")

            # Audit failure
            await self.audit_service.record_event(
                event_type=AuditEventType.NOTIFICATION_FAILED,
                actor_type=AuditActorType.SYSTEM,
                user_id=user_id,
                document_id=document_id,
                event_data={"type": type, "recipient": recipient_email, "error": final_error}
            )

        # 4. Commit to ensure notification state is persisted
        await self.session.commit()

        return notification

    async def retry_failed_notifications(self) -> int:
        """
        Attempts to redeliver all notifications that are currently in FAILED status.
        Returns the count of successfully redelivered notifications.
        """
        failed = await self.repo.get_by_status(NotificationStatus.FAILED)
        success_count = 0

        for notif in failed:
            try:
                success = await self.provider.send_email(notif.recipient_email, notif.subject, notif.body)
                if success:
                    await self.repo.update_status(notif.id, NotificationStatus.SENT)
                    success_count += 1
            except Exception:
                pass

        if success_count > 0:
            await self.session.commit()

        return success_count
