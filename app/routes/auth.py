"""Authentication routes: registration, login, and profile retrieval."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import authenticate_user, build_token_for_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new citizen or municipality admin account",
    description="Creates a new user account and immediately returns a JWT access token.",
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = register_user(db, payload)
    token = build_token_for_user(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
    description="Validates credentials and returns a JWT access token plus the user's profile.",
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload)
    token = build_token_for_user(user)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get the current authenticated user's profile",
)
def profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
