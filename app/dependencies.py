"""
FastAPI dependencies for authentication and role-based access control.

Usage in a route:
    @router.get("/admin-only")
    def handler(user: User = Depends(require_role(UserRole.MUNICIPALITY_ADMIN))):
        ...
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.constants import UserRole
from app.utils.security import decode_access_token

COOKIE_NAME = "access_token"


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    Same as OAuth2PasswordBearer, but falls back to reading the token
    from an httponly cookie if no Authorization header is present.
    Keeps Swagger UI's "Authorize" button working via the header,
    while allowing cookie-based auth for the frontend.
    """

    async def __call__(self, request: Request) -> str | None:
        header_token = await super(OAuth2PasswordBearerWithCookie, self).__call__(request)
        if header_token:
            return header_token

        cookie_value = request.cookies.get(COOKIE_NAME)
        if cookie_value:
            scheme, _, param = cookie_value.partition(" ")
            if scheme.lower() == "bearer" and param:
                return param

        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="api/v1/auth/login", auto_error=False)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Decode the bearer token and load the corresponding User, or raise 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def require_role(*allowed_roles: UserRole):
    """Dependency factory: restricts a route to one or more roles."""

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


# Convenience pre-built dependency for the common "admin only" case.
require_municipality_admin = require_role(UserRole.MUNICIPALITY_ADMIN)