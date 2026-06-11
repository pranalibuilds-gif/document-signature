from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db, get_current_user
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import LoginRequest, TokenResponse, RefreshRequest, VerifyEmailRequest, ForgotPasswordRequest, ResetPasswordRequest
from app.modules.users.schemas import UserCreate, UserRead
from app.modules.users.models import User
from app.common.enums import NotificationType
from app.core.rate_limit import limiter
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.register(user_in)
    await db.commit()

    # Send verification email post-commit
    if hasattr(user, "_verification_token"):
        link = f"http://localhost:3000/verify-email?token={user._verification_token}"
        await auth_service.notification_service.send_notification(
            recipient_email=user.email,
            subject="Verify your email",
            body=f"Welcome! Please verify your email: {link}",
            type=NotificationType.INVITATION, # We can use specialized type if needed
            user_id=user.id
        )

    return user

@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    verify_in: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    await auth_service.verify_email(verify_in.token)
    await db.commit()
    return {"message": "Email verified successfully"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    forgot_in: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    raw_token = await auth_service.forgot_password(forgot_in.email)
    await db.commit()

    if raw_token:
        link = f"http://localhost:3000/reset-password?token={raw_token}"
        await auth_service.notification_service.send_notification(
            recipient_email=forgot_in.email,
            subject="Reset your password",
            body=f"Please use the following link to reset your password: {link}. This link expires in 1 hour.",
            type=NotificationType.REMINDER
        )

    # Always return success to prevent email enumeration
    return {"message": "If an account exists with that email, a reset link has been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    reset_in: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    await auth_service.reset_password(reset_in.token, reset_in.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}

@router.post("/resend-verification", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    auth_service = AuthService(db)
    raw_token = await auth_service.resend_verification(current_user)
    await db.commit()

    if raw_token:
        link = f"http://localhost:3000/verify-email?token={raw_token}"
        await auth_service.notification_service.send_notification(
            recipient_email=current_user.email,
            subject="Verify your email",
            body=f"Please verify your email: {link}",
            type=NotificationType.INVITATION,
            user_id=current_user.id
        )

    return {"message": "Verification email resent"}

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    tokens = await auth_service.login(login_data)
    await db.commit()
    return tokens

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh(request: Request, refresh_data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    tokens = await auth_service.refresh(refresh_data.refresh_token)
    await db.commit()
    return tokens

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(refresh_data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    await auth_service.logout(refresh_data.refresh_token)
    await db.commit()
