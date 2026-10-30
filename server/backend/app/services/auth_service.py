from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.admin import AdminUser
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedHTTP, BadRequestHTTP, QuotaExceededException, SubscriptionExpiredException


class AuthService:
    @staticmethod
    def is_setup_required(db: Session) -> bool:
        """Returns True if no admin accounts exist."""
        return db.query(AdminUser).count() == 0

    @staticmethod
    def initialize_superadmin(db: Session, username: str, password: str) -> AdminUser:
        if not AuthService.is_setup_required(db):
            raise BadRequestHTTP("System is already initialized.")
        
        admin = AdminUser(
            username=username.strip(),
            password_hash=get_password_hash(password),
            role="superadmin",
            created_at=datetime.now(timezone.utc)
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def authenticate_admin(db: Session, username: str, password: str) -> AdminUser:
        admin = db.query(AdminUser).filter(AdminUser.username == username.strip()).first()
        if not admin or not verify_password(password, admin.password_hash):
            raise UnauthorizedHTTP("Invalid admin credentials")
        
        admin.last_login = datetime.now(timezone.utc)
        db.commit()
        return admin

    @staticmethod
    def authenticate_client(db: Session, username: str, password: str) -> User:
        user = db.query(User).filter(User.username == username.strip()).first()
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedHTTP("Invalid client credentials")
        
        if not user.is_active:
            raise UnauthorizedHTTP("Account is disabled")
        
        if user.is_expired:
            raise SubscriptionExpiredException("Your subscription has expired")
        
        if user.is_quota_depleted:
            raise QuotaExceededException("Your traffic quota has been exhausted")
        
        return user

