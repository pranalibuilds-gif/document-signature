import logging
from app.core.database import AsyncSessionLocal
from app.modules.signers.repository import SignerRepository
from app.modules.auth.repository import AuthRepository
from app.core.logging import logger

async def cleanup_tokens_job():
    logger.info("Starting token cleanup job...")
    async with AsyncSessionLocal() as session:
        try:
            signer_repo = SignerRepository(session)
            auth_repo = AuthRepository(session)
            from app.modules.auth.repository import EmailVerificationRepository
            verify_repo = EmailVerificationRepository(session)

            signing_count = await signer_repo.cleanup_expired_signing_tokens(retention_days=90)
            refresh_count = await auth_repo.cleanup_expired_refresh_tokens(retention_days=30)
            verify_count = await verify_repo.cleanup_expired_tokens(retention_days=7)

            await session.commit()
            logger.info(f"Cleanup finished. Deleted {signing_count} signing, {refresh_count} refresh, and {verify_count} verification tokens.")

        except Exception as e:
            logger.error(f"Error in cleanup_tokens_job: {e}")
            await session.rollback()
