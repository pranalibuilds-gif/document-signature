import asyncio
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def run():
    async with AsyncSessionLocal() as s:
        # Direct SQL to avoid ORM initialization issues in standalone scripts
        res = await s.execute(text("SELECT id FROM document_signers WHERE email = 'signer@example.com'"))
        signer_id = res.scalar()

        if not signer_id:
            print("Signer not found")
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)

        await s.execute(
            text("INSERT INTO signing_tokens (id, document_signer_id, token_hash, expires_at, created_at, updated_at) "
                 "VALUES (gen_random_uuid(), :sid, :hash, :exp, now(), now())"),
            {"sid": signer_id, "hash": token_hash, "exp": expires_at}
        )
        await s.commit()
        print(f"RAW_TOKEN:{raw_token}")

if __name__ == "__main__":
    asyncio.run(run())
