import uuid
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.notifications.models import Notification
from app.common.enums import NotificationStatus

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_by_status(self, status: NotificationStatus) -> list[Notification]:
        result = await self.session.execute(
            select(Notification).where(Notification.status == status)
        )
        return list(result.scalars().all())

    async def update_status(
        self,
        notification_id: uuid.UUID,
        status: NotificationStatus,
        error_message: str | None = None
    ) -> None:
        values = {"status": status, "updated_at": datetime.now(timezone.utc)}
        if status == NotificationStatus.SENT:
            values["sent_at"] = datetime.now(timezone.utc)
        if error_message:
            values["error_message"] = error_message

        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(**values)
        )
