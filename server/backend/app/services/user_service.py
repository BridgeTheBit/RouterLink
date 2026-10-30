from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.session import Session as VPNSession
from app.schemas.user import UserCreate, UserUpdate, UserQuotaUpdate
from app.core.security import get_password_hash
from app.core.exceptions import BadRequestHTTP, NotFoundHTTP


class UserService:
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
        query = db.query(User)
        if search:
            query = query.filter(User.username.ilike(f"%{search.strip()}%"))
        return query.order_by(User.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundHTTP(f"User with ID {user_id} not found")
        return user

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username.strip()).first()

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        existing = UserService.get_by_username(db, user_in.username)
        if existing:
            raise BadRequestHTTP(f"Username '{user_in.username}' already exists")

        user = User(
            username=user_in.username.strip(),
            password_hash=get_password_hash(user_in.password),
            email=user_in.email,
            is_active=user_in.is_active,
            traffic_limit_bytes=user_in.traffic_limit_bytes,
            used_traffic_bytes=0,
            subscription_start=datetime.now(timezone.utc),
            expires_at=user_in.expires_at,
            max_concurrent_connections=user_in.max_concurrent_connections,
            max_registered_devices=user_in.max_registered_devices,
            allowed_protocols=user_in.allowed_protocols,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_in: UserUpdate) -> User:
        user = UserService.get_by_id(db, user_id)

        if user_in.email is not None:
            user.email = user_in.email
        if user_in.is_active is not None:
            user.is_active = user_in.is_active
        if user_in.traffic_limit_bytes is not None:
            user.traffic_limit_bytes = user_in.traffic_limit_bytes
        if user_in.expires_at is not None:
            user.expires_at = user_in.expires_at
        if user_in.max_concurrent_connections is not None:
            user.max_concurrent_connections = user_in.max_concurrent_connections
        if user_in.max_registered_devices is not None:
            user.max_registered_devices = user_in.max_registered_devices
        if user_in.allowed_protocols is not None:
            user.allowed_protocols = user_in.allowed_protocols
        if user_in.password:
            user.password_hash = get_password_hash(user_in.password)

        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_quota(db: Session, user_id: int, quota_in: UserQuotaUpdate) -> User:
        user = UserService.get_by_id(db, user_id)

        if quota_in.reset_used_traffic:
            user.used_traffic_bytes = 0

        if quota_in.additional_traffic_bytes:
            user.traffic_limit_bytes += quota_in.additional_traffic_bytes

        if quota_in.new_traffic_limit_bytes is not None:
            user.traffic_limit_bytes = quota_in.new_traffic_limit_bytes

        if quota_in.new_expires_at is not None:
            user.expires_at = quota_in.new_expires_at

        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_by_id(db, user_id)
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def get_active_sessions_count(db: Session, user_id: int) -> int:
        return db.query(VPNSession).filter(
            VPNSession.user_id == user_id,
            VPNSession.is_active == True
        ).count()

