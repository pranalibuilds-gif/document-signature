from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.users.models import User
from app.modules.documents.models import Document
from app.modules.notifications.models import Notification
from app.common.enums import DocumentStatus, NotificationStatus

class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def count_users(self, verified_only: bool = False) -> int:
        stmt = select(func.count()).select_from(User)
        if verified_only:
            stmt = stmt.where(User.is_verified == True)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_documents(self, status: DocumentStatus | None = None) -> int:
        stmt = select(func.count()).select_from(Document)
        if status:
            stmt = stmt.where(Document.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_notifications(self, status: NotificationStatus | None = None) -> int:
        stmt = select(func.count()).select_from(Notification)
        if status:
            stmt = stmt.where(Notification.status == status)
        result = await self.session.execute(stmt)
        return result.scalar_one()
