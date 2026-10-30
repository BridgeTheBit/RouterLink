from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserQuotaUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Admin - Users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    users = UserService.get_users(db, skip=skip, limit=limit, search=search)
    results = []
    for u in users:
        active_count = UserService.get_active_sessions_count(db, u.id)
        # Parse into response model
        resp = UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_active=u.is_active,
            traffic_limit_bytes=u.traffic_limit_bytes,
            used_traffic_bytes=u.used_traffic_bytes,
            remaining_traffic_bytes=u.remaining_traffic_bytes,
            is_expired=u.is_expired,
            is_quota_depleted=u.is_quota_depleted,
            can_connect=u.can_connect,
            subscription_start=u.subscription_start,
            expires_at=u.expires_at,
            max_concurrent_connections=u.max_concurrent_connections,
            max_registered_devices=u.max_registered_devices,
            allowed_protocols=u.allowed_protocols,
            created_at=u.created_at,
            updated_at=u.updated_at,
            active_sessions_count=active_count
        )
        results.append(resp)
    return results


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    u = UserService.create_user(db, payload)
    return UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        traffic_limit_bytes=u.traffic_limit_bytes,
        used_traffic_bytes=u.used_traffic_bytes,
        remaining_traffic_bytes=u.remaining_traffic_bytes,
        is_expired=u.is_expired,
        is_quota_depleted=u.is_quota_depleted,
        can_connect=u.can_connect,
        subscription_start=u.subscription_start,
        expires_at=u.expires_at,
        max_concurrent_connections=u.max_concurrent_connections,
        max_registered_devices=u.max_registered_devices,
        allowed_protocols=u.allowed_protocols,
        created_at=u.created_at,
        updated_at=u.updated_at,
        active_sessions_count=0
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    u = UserService.get_by_id(db, user_id)
    active_count = UserService.get_active_sessions_count(db, u.id)
    return UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        traffic_limit_bytes=u.traffic_limit_bytes,
        used_traffic_bytes=u.used_traffic_bytes,
        remaining_traffic_bytes=u.remaining_traffic_bytes,
        is_expired=u.is_expired,
        is_quota_depleted=u.is_quota_depleted,
        can_connect=u.can_connect,
        subscription_start=u.subscription_start,
        expires_at=u.expires_at,
        max_concurrent_connections=u.max_concurrent_connections,
        max_registered_devices=u.max_registered_devices,
        allowed_protocols=u.allowed_protocols,
        created_at=u.created_at,
        updated_at=u.updated_at,
        active_sessions_count=active_count
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    u = UserService.update_user(db, user_id, payload)
    active_count = UserService.get_active_sessions_count(db, u.id)
    return UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        traffic_limit_bytes=u.traffic_limit_bytes,
        used_traffic_bytes=u.used_traffic_bytes,
        remaining_traffic_bytes=u.remaining_traffic_bytes,
        is_expired=u.is_expired,
        is_quota_depleted=u.is_quota_depleted,
        can_connect=u.can_connect,
        subscription_start=u.subscription_start,
        expires_at=u.expires_at,
        max_concurrent_connections=u.max_concurrent_connections,
        max_registered_devices=u.max_registered_devices,
        allowed_protocols=u.allowed_protocols,
        created_at=u.created_at,
        updated_at=u.updated_at,
        active_sessions_count=active_count
    )


@router.post("/{user_id}/quota", response_model=UserResponse)
def update_user_quota(
    user_id: int,
    payload: UserQuotaUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    u = UserService.update_quota(db, user_id, payload)
    active_count = UserService.get_active_sessions_count(db, u.id)
    return UserResponse(
        id=u.id,
        username=u.username,
        email=u.email,
        is_active=u.is_active,
        traffic_limit_bytes=u.traffic_limit_bytes,
        used_traffic_bytes=u.used_traffic_bytes,
        remaining_traffic_bytes=u.remaining_traffic_bytes,
        is_expired=u.is_expired,
        is_quota_depleted=u.is_quota_depleted,
        can_connect=u.can_connect,
        subscription_start=u.subscription_start,
        expires_at=u.expires_at,
        max_concurrent_connections=u.max_concurrent_connections,
        max_registered_devices=u.max_registered_devices,
        allowed_protocols=u.allowed_protocols,
        created_at=u.created_at,
        updated_at=u.updated_at,
        active_sessions_count=active_count
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    UserService.delete_user(db, user_id)
    return None

