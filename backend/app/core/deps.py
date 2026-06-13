"""
Dependency injection for FastAPI routes.
Handles database session lifecycle and JWT authentication logic.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.security.jwt import decode_token
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.common.enums import UserRole
from app.core.logging import logger

# Tells FastAPI where to look for the access token in the request headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a new database session for a request and ensures it is closed after.
    Used as a Depends(get_db) in route handlers.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Authenticates a user based on the provided JWT access token.
    Checks token validity, user existence, and account status.
    """
    payload = decode_token(token)
    user_id = payload.get("sub")

    # Check if token exists and is an 'access' type token
    if not user_id or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_repo = UserRepository(db)
    try:
        from uuid import UUID
        # JWT subject is stored as a string; database requires a UUID object for comparison.
        target_id = UUID(user_id) if isinstance(user_id, str) else user_id
        user = await user_repo.get_by_id(target_id)
    except (ValueError, TypeError, Exception) as e:
        logger.error(f"Error resolving user from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Restricts access to routes to only users with the ADMIN role.
    Must be used in combination with get_current_user.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return user
