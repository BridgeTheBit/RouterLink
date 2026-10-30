from datetime import timedelta
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.schemas.auth import (
    SetupRequest,
    LoginRequest,
    TokenResponse,
    SetupStatusResponse
)
from app.services.auth_service import AuthService
from app.core.security import create_access_token
from app.core.exceptions import BadRequestHTTP

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/setup/status", response_model=SetupStatusResponse)
def get_setup_status(db: Session = Depends(get_db)):
    """Check if the system requires first-time admin setup."""
    is_required = AuthService.is_setup_required(db)
    return SetupStatusResponse(
        is_setup_required=is_required,
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION
    )


@router.post("/setup", response_model=TokenResponse)
def setup_superadmin(payload: SetupRequest, db: Session = Depends(get_db)):
    """Initialize the initial master administrator account."""
    if payload.password != payload.confirm_password:
        raise BadRequestHTTP("Passwords do not match")

    admin = AuthService.initialize_superadmin(db, payload.username, payload.password)
    token = create_access_token(
        subject=admin.username,
        role=admin.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=admin.role,
        username=admin.username,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=TokenResponse)
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate administrator and return access JWT token."""
    admin = AuthService.authenticate_admin(db, payload.username, payload.password)
    token = create_access_token(
        subject=admin.username,
        role=admin.role,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=admin.role,
        username=admin.username,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

