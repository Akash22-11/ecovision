"""
Password hashing and JWT helpers.

Kept separate from `services/auth_service.py`: this module is pure,
side-effect-free crypto/token logic, while auth_service.py orchestrates
DB lookups and business rules around it.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: typically the user's id (as string).
        role: the user's role, embedded as a claim for RBAC checks.
        expires_minutes: overrides the default token lifetime from settings.

    Returns:
        Encoded JWT string.
    """
    expire_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "exp": expire_at,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Raises:
        JWTError: if the token is invalid, malformed, or expired.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as exc:
        raise JWTError(f"Could not validate token: {exc}") from exc
