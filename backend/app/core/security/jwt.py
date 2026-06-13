"""
JWT Token generation and decoding logic.
Handles both short-lived access tokens and long-lived refresh tokens.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import jwt, JWTError
from app.core.config import settings

def create_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token for authentication.
    :param subject: The user ID (stored in 'sub' claim)
    :param expires_delta: Optional custom expiration time
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "access", # Differentiates from refresh tokens
        "jti": str(uuid.uuid4()), # Unique ID for this specific token instance
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT refresh token for session rotation.
    Has a longer expiration than the access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Verifies and decodes a JWT token string.
    Returns the payload dictionary if valid, or an empty dict if invalid/expired.
    """
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_token
    except JWTError:
        return {} # Token validation failed (expired, tampered, etc.)
