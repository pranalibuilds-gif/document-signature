import logging
from app.modules.notifications.providers.base import EmailProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class MailtrapProvider(EmailProvider):
    async def send_email(self, recipient: str, subject: str, body: str) -> bool:
        # In a real implementation, this would use aiosmtplib with settings.MAIL_SERVER etc.
        # For Phase 2.4, we simulate the delivery mechanism.

        if not settings.MAIL_SERVER or settings.MAIL_SERVER == "smtp.mailtrap.io":
            logger.info(f"[MOCK EMAIL] To: {recipient} | Subject: {subject}")
            logger.info(f"[MOCK EMAIL] Body: {body[:100]}...")
            return True

        # Here you would implement real SMTP logic
        logger.warning("MailtrapProvider: Real SMTP not implemented yet.")
        return False
