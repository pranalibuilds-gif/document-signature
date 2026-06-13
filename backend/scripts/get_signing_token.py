import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.signers.models import SigningToken, DocumentSigner
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as s:
        # Join SigningToken with DocumentSigner to find by email
        q = select(SigningToken.token_hash, DocumentSigner.email).join(DocumentSigner).where(DocumentSigner.email == 'signer@example.com')
        r = await s.execute(q)
        # Note: token_hash is stored, raw token is not.
        # I'll need to check notifications or audit logs for the RAW token.
        from app.modules.notifications.models import Notification
        r_notif = await s.execute(select(Notification).where(Notification.recipient_email == 'signer@example.com').order_by(Notification.created_at.desc()))
        notif = r_notif.scalar_one_or_none()
        if notif:
            print(f"Notification Subject: {notif.subject}")
            # We don't have body in DB. I'll check logs.
        else:
            print("No notification found")

if __name__ == "__main__":
    asyncio.run(run())
