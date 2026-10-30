from typing import Optional
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedHTTP, ForbiddenHTTP
from app.models.admin import AdminUser
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_current_admin(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    if not token:
        raise UnauthorizedHTTP("Authentication required")

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedHTTP("Invalid or expired authentication token")

    username: str = payload.get("sub")
    role: str = payload.get("role")

    if not username or role not in ["superadmin", "admin"]:
        raise ForbiddenHTTP("Administrative privileges required")

    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        raise UnauthorizedHTTP("Admin user does not exist")

    return admin


def get_current_client(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not token:
        raise UnauthorizedHTTP("Authentication required")

    payload = decode_token(token)
    if not payload:
        raise UnauthorizedHTTP("Invalid or expired authentication token")

    username: str = payload.get("sub")
    role: str = payload.get("role")

    if not username or role != "client":
        raise ForbiddenHTTP("Invalid client authorization")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise UnauthorizedHTTP("User does not exist")

    if not user.is_active:
        raise ForbiddenHTTP("Account is disabled")

    return user

