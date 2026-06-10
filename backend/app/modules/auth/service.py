import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository import UserRepository
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.auth.repository import AuthRepository
from app.modules.auth.models import RefreshToken
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import settings

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.auth_repo = AuthRepository(session)

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def register(self, user_in: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )

        hashed_pw = hash_password(user_in.password)
        user = User(
            email=user_in.email,
            hashed_password=hashed_pw,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
        )
        return await self.user_repo.create(user)

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        return await self._create_token_pair(user)

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        token_hash = self._hash_token(refresh_token_str)
        db_token = await self.auth_repo.get_refresh_token_by_hash(token_hash)

        if not db_token or db_token.revoked_at or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired or revoked",
            )

        user = await self.user_repo.get_by_id(db_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Rotate: revoke old one
        await self.auth_repo.revoke_refresh_token(db_token.id)

        return await self._create_token_pair(user)

    async def logout(self, refresh_token_str: str) -> None:
        token_hash = self._hash_token(refresh_token_str)
        db_token = await self.auth_repo.get_refresh_token_by_hash(token_hash)
        if db_token:
            await self.auth_repo.revoke_refresh_token(db_token.id)

    async def _create_token_pair(self, user: User) -> TokenResponse:
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        # Store refresh token hash
        token_hash = self._hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        await self.auth_repo.create_refresh_token(db_refresh_token)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
