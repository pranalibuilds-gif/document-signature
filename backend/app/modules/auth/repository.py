import uuid
from datetime import datetime, timezone
from sqlalchemy import select, update, delete, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.auth.models import RefreshToken

class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token

    async def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def cleanup_expired_refresh_tokens(self, retention_days: int = 30) -> int:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        retention_threshold = now - timedelta(days=retention_days)

        stmt = delete(RefreshToken).where(
            or_(
                and_(RefreshToken.expires_at < now, RefreshToken.created_at < retention_threshold),
                and_(RefreshToken.revoked_at.is_not(None), RefreshToken.revoked_at < retention_threshold)
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount
