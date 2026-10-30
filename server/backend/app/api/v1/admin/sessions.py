from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.schemas.session import SessionResponse, DisconnectResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Admin - Sessions"])


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    active_only: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    sessions = SessionService.list_sessions(db, active_only=active_only, skip=skip, limit=limit)
    results = []
    for s in sessions:
        results.append(SessionResponse(
            id=s.id,
            user_id=s.user_id,
            username=s.user.username if s.user else None,
            device_name=s.device.device_name if s.device else "Unknown",
            protocol=s.protocol,
            client_ip=s.client_ip,
            assigned_vpn_ip=s.assigned_vpn_ip,
            upload_bytes=s.upload_bytes,
            download_bytes=s.download_bytes,
            total_bytes=s.total_bytes,
            duration_seconds=s.duration_seconds,
            connected_at=s.connected_at,
            is_active=s.is_active
        ))
    return results


@router.post("/{session_id}/terminate", response_model=DisconnectResponse)
def terminate_session(
    session_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    SessionService.terminate_session(db, session_id)
    return DisconnectResponse(
        success=True,
        message=f"Session {session_id} successfully terminated",
        session_id=session_id
    )

