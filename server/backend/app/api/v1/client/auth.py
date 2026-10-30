from datetime import timedelta
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.core.dependencies import get_current_client
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.services.user_service import UserService

router = APIRouter(prefix="/client", tags=["Client - Mobile API"])


@router.post("/login", response_model=TokenResponse)
def client_login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates Android Client and returns client-scoped JWT token."""
    user = AuthService.authenticate_client(db, payload.username, payload.password)
    token = create_access_token(
        subject=user.username,
        role="client",
        expires_delta=timedelta(minutes=settings.CLIENT_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role="client",
        username=user.username,
        expires_in=settings.CLIENT_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/profile", response_model=UserResponse)
def get_client_profile(
    user: User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    """Returns current user quota, expiration, and authorized protocols."""
    active_count = UserService.get_active_sessions_count(db, user.id)
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        traffic_limit_bytes=user.traffic_limit_bytes,
        used_traffic_bytes=user.used_traffic_bytes,
        remaining_traffic_bytes=user.remaining_traffic_bytes,
        is_expired=user.is_expired,
        is_quota_depleted=user.is_quota_depleted,
        can_connect=user.can_connect,
        subscription_start=user.subscription_start,
        expires_at=user.expires_at,
        max_concurrent_connections=user.max_concurrent_connections,
        max_registered_devices=user.max_registered_devices,
        allowed_protocols=user.allowed_protocols,
        created_at=user.created_at,
        updated_at=user.updated_at,
        active_sessions_count=active_count
    )

