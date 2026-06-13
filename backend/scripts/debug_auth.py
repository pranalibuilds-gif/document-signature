import asyncio
from app.core.database import AsyncSessionLocal
from app.modules.users.models import User
from app.core.security.hashing import hash_password, verify_password
from app.common.enums import UserRole
from sqlalchemy import select
from uuid import UUID

async def debug():
    async with AsyncSessionLocal() as s:
        # 1. Check user existence
        r = await s.execute(select(User).where(User.email == 'pranali@demo.com'))
        user = r.scalar_one_or_none()

        if not user:
            print("User pranali@demo.com NOT FOUND in DB.")
            return

        print(f"User Found: {user.email}")
        print(f"User ID: {user.id} (Type: {type(user.id)})")
        print(f"Is Active: {user.is_active}")
        print(f"Is Verified: {user.is_verified}")

        # 2. Test password verification
        test_pw = "Pranali123!"
        match = verify_password(test_pw, user.hashed_password)
        print(f"Password '{test_pw}' matches: {match}")

        # 3. Update password to something simpler as requested
        new_pw = "pranali25"
        user.hashed_password = hash_password(new_pw)
        await s.commit()
        print(f"Password updated to: {new_pw}")

if __name__ == "__main__":
    asyncio.run(debug())
