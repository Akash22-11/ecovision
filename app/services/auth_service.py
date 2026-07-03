"""Auth service: orchestrates user registration, login, and profile retrieval."""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserLoginRequest, UserRegisterRequest
from app.utils.logger import logger
from app.utils.security import create_access_token, hash_password, verify_password
from app.utils.validators import ValidationError


def register_user(db: Session, payload: UserRegisterRequest) -> User:
    """Create a new user account. Raises ValidationError if the email is taken."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise ValidationError("An account with this email already exists.", status_code=409)

    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Registered new user: {user.email} (role={user.role})")
    return user


def authenticate_user(db: Session, payload: UserLoginRequest) -> User:
    """Validate credentials and return the User. Raises ValidationError on failure."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        logger.warning(f"Failed login attempt for email: {payload.email}")
        raise ValidationError("Invalid email or password.", status_code=401)

    logger.info(f"User logged in: {user.email}")
    return user


def build_token_for_user(user: User) -> str:
    """Issue a JWT access token for an authenticated user."""
    return create_access_token(subject=str(user.id), role=user.role.value)
