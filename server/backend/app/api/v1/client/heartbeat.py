from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_client
from app.models.user import User
from app.models.session import Session as VPNSession
from app.services.session_service import SessionService

router = APIRouter(prefix="/client", tags=["Client - Heartbeat"])


class HeartbeatRequest(BaseModel):
    session_token: Optional[str] = None
    device_id: str
    device_name: Optional[str] = "Android Phone"
    protocol: str = "openvpn_tcp"
    upload_delta_bytes: int = Field(0, ge=0)
    download_delta_bytes: int = Field(0, ge=0)


class HeartbeatResponse(BaseModel):
    session_token: str
    can_continue: bool
    status: str # active, quota_depleted, expired, concurrent_limit_exceeded
    remaining_traffic_bytes: Optional[int]
    used_traffic_bytes: int
    is_expired: bool


@router.post("/heartbeat", response_model=HeartbeatResponse)
def client_heartbeat(
    payload: HeartbeatRequest,
    user: User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    session_obj = None
    if payload.session_token:
        session_obj = db.query(VPNSession).filter(
            VPNSession.session_token == payload.session_token,
            VPNSession.user_id == user.id,
            VPNSession.is_active == True
        ).first()

    # If no existing active session found, attempt to start one
    if not session_obj:
        try:
            session_obj = SessionService.start_session(
                db=db,
                user_id=user.id,
                protocol=payload.protocol,
                device_id_str=payload.device_id,
                device_name=payload.device_name
            )
        except Exception as e:
            return HeartbeatResponse(
                session_token="",
                can_continue=False,
                status="concurrent_limit_exceeded",
                remaining_traffic_bytes=user.remaining_traffic_bytes,
                used_traffic_bytes=user.used_traffic_bytes,
                is_expired=user.is_expired
            )

    # Record traffic delta if any
    if payload.upload_delta_bytes > 0 or payload.download_delta_bytes > 0:
        session_obj = SessionService.record_traffic(
            db=db,
            session_id=session_obj.id,
            upload_delta=payload.upload_delta_bytes,
            download_delta=payload.download_delta_bytes
        )

    # Re-evaluate user status
    if not user.can_connect:
        status_reason = "quota_depleted" if user.is_quota_depleted else ("expired" if user.is_expired else "disabled")
        return HeartbeatResponse(
            session_token=session_obj.session_token,
            can_continue=False,
            status=status_reason,
            remaining_traffic_bytes=user.remaining_traffic_bytes,
            used_traffic_bytes=user.used_traffic_bytes,
            is_expired=user.is_expired
        )

    return HeartbeatResponse(
        session_token=session_obj.session_token,
        can_continue=True,
        status="active",
        remaining_traffic_bytes=user.remaining_traffic_bytes,
        used_traffic_bytes=user.used_traffic_bytes,
        is_expired=user.is_expired
    )

