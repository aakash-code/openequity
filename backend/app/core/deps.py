"""
Dependencies for FastAPI routes
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User

security = HTTPBearer()


def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        db: Database session
        credentials: HTTP Authorization credentials with JWT token

    Returns:
        Current user

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user with admin role

    Args:
        current_user: Current user from get_current_user

    Returns:
        Current admin user

    Raises:
        HTTPException: If user is not admin
    """
    from app.models.user import UserRole

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_user_ws(
    token: str,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from WebSocket token (query parameter)

    Args:
        token: JWT token from query parameter
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None

        email: str = payload.get("sub")
        if email is None:
            return None

        user = db.query(User).filter(User.email == email).first()
        if user is None or not user.is_active:
            return None

        return user
    except Exception:
        return None
