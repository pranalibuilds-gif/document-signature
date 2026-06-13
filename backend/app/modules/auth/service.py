"""
Service layer for Authentication and User management.
Handles registration, login, password resets, and email verification.
"""
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.repository import UserRepository
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.modules.auth.repository import AuthRepository, EmailVerificationRepository, PasswordResetRepository
from app.modules.auth.models import RefreshToken, EmailVerificationToken, PasswordResetToken
from app.modules.auth.schemas import LoginRequest, TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.modules.audit.service import AuditService
from app.modules.notifications.service import NotificationService
from app.common.enums import AuditActorType, AuditEventType
from app.core.security.hashing import hash_password, verify_password
from app.core.security.jwt import create_access_token, create_refresh_token, decode_token
from app.core.config import settings
from app.core.logging import logger

class AuthService:
    def __init__(self, session: AsyncSession):
        """Initializes repositories and dependent services."""
        self.session = session
        self.user_repo = UserRepository(session)
        self.auth_repo = AuthRepository(session)
        self.verification_repo = EmailVerificationRepository(session)
        self.password_reset_repo = PasswordResetRepository(session)
        self.audit_service = AuditService(session)
        self.notification_service = NotificationService(session)

    def _hash_token(self, token: str) -> str:
        """Helper to create a secure hash of raw tokens before storing in DB."""
        return hashlib.sha256(token.encode()).hexdigest()

    async def register(self, user_in: UserCreate) -> User:
        """
        Creates a new user account.
        Checks for email duplicates, hashes the password, and creates a verification token.
        """
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
            role=user_in.role
        )
        created_user = await self.user_repo.create(user)
        logger.info(f"User registered successfully: {created_user.email}")

        # Log the security event
        await self.audit_service.record_event(
            event_type=AuditEventType.USER_REGISTERED,
            actor_type=AuditActorType.USER,
            user_id=created_user.id,
            event_data={"email": created_user.email}
        )

        # Prepare email verification link
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)

        db_token = EmailVerificationToken(
            user_id=created_user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        await self.verification_repo.create(db_token)

        # raw_token is not saved in DB, only the hash is.
        # We attach it to the object temporarily so the router can send it in an email.
        created_user._verification_token = raw_token

        return created_user

    async def verify_email(self, token_str: str) -> None:
        """Validates an email verification token and marks the user as verified."""
        token_hash = self._hash_token(token_str)
        db_token = await self.verification_repo.get_by_hash(token_hash)

        if not db_token or db_token.used_at or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        user = await self.user_repo.get_by_id(db_token.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_verified:
            user.is_verified = True
            await self.session.flush() # Persist change to user
            logger.info(f"Email verified for user: {user.email}")

            await self.audit_service.record_event(
                event_type=AuditEventType.EMAIL_VERIFIED,
                actor_type=AuditActorType.USER,
                user_id=user.id
            )

        db_token.used_at = datetime.now(timezone.utc) # Burn the token

    async def forgot_password(self, email: str) -> str:
        """Starts the password reset flow. Returns a raw token if user exists."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return "" # Return empty to prevent user enumeration attacks

        # Invalidate any existing active reset tokens for this user
        await self.password_reset_repo.invalidate_user_tokens(user.id)

        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        db_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        await self.password_reset_repo.create(db_token)
        return raw_token

    async def reset_password(self, token_str: str, new_password: str) -> None:
        """Validates a reset token and updates the user's password."""
        token_hash = self._hash_token(token_str)
        db_token = await self.password_reset_repo.get_by_hash(token_hash)

        if not db_token or db_token.used_at or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        user = await self.user_repo.get_by_id(db_token.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.hashed_password = hash_password(new_password)
        db_token.used_at = datetime.now(timezone.utc)

        await self.audit_service.record_event(
            event_type=AuditEventType.USER_UPDATED,
            actor_type=AuditActorType.USER,
            user_id=user.id,
            event_data={"action": "password_reset"}
        )

    async def resend_verification(self, user: User) -> str:
        """Generates a new verification token for an unverified user."""
        if user.is_verified:
            return ""

        await self.verification_repo.invalidate_user_tokens(user.id)

        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS)

        db_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        await self.verification_repo.create(db_token)

        await self.audit_service.record_event(
            event_type=AuditEventType.EMAIL_VERIFICATION_SENT,
            actor_type=AuditActorType.USER,
            user_id=user.id,
            event_data={"email": user.email}
        )

        return raw_token

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """Authenticates user credentials and returns a new Access/Refresh token pair."""
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        token_pair = await self._create_token_pair(user)
        logger.info(f"User login successful: {user.email}")

        await self.audit_service.record_event(
            event_type=AuditEventType.USER_LOGIN,
            actor_type=AuditActorType.USER,
            user_id=user.id,
            event_data={"email": user.email}
        )

        return token_pair

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Rotates an existing refresh token for a new token pair."""
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

        # Token Rotation: Revoke the old token immediately
        await self.auth_repo.revoke_refresh_token(db_token.id)

        # Issue a brand new pair
        return await self._create_token_pair(user)

    async def logout(self, refresh_token_str: str) -> None:
        """Revokes a refresh token to end a user session."""
        token_hash = self._hash_token(refresh_token_str)
        db_token = await self.auth_repo.get_refresh_token_by_hash(token_hash)
        if db_token:
            await self.auth_repo.revoke_refresh_token(db_token.id)

    async def _create_token_pair(self, user: User) -> TokenResponse:
        """Generates access and refresh tokens and stores the refresh token hash."""
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

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
