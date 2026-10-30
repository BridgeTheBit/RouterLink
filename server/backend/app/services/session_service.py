from datetime import datetime, timezone
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.session import Session as VPNSession
from app.models.user import User
from app.models.device import Device
from app.core.exceptions import ConcurrentLimitException, NotFoundHTTP, BadRequestHTTP


class SessionService:
    @staticmethod
    def list_sessions(db: Session, active_only: bool = True, skip: int = 0, limit: int = 100) -> List[VPNSession]:
        query = db.query(VPNSession)
        if active_only:
            query = query.filter(VPNSession.is_active == True)
        return query.order_by(VPNSession.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def start_session(
        db: Session,
        user_id: int,
        protocol: str,
        client_ip: Optional[str] = None,
        assigned_vpn_ip: Optional[str] = None,
        device_id_str: Optional[str] = None,
        device_name: Optional[str] = None
    ) -> VPNSession:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.can_connect:
            raise BadRequestHTTP("User is inactive, expired, or quota depleted")

        # Check concurrent connection limit
        active_count = db.query(VPNSession).filter(
            VPNSession.user_id == user_id,
            VPNSession.is_active == True
        ).count()

        if active_count >= user.max_concurrent_connections:
            raise ConcurrentLimitException(
                f"Maximum concurrent connections ({user.max_concurrent_connections}) reached for this account."
            )

        # Register or update device
        device_obj = None
        if device_id_str:
            device_obj = db.query(Device).filter(Device.device_id == device_id_str).first()
            if not device_obj:
                device_obj = Device(
                    user_id=user_id,
                    device_id=device_id_str,
                    device_name=device_name or "Android Device",
                    platform="android",
                    first_seen=datetime.now(timezone.utc),
                    last_seen=datetime.now(timezone.utc)
                )
                db.add(device_obj)
                db.commit()
                db.refresh(device_obj)
            else:
                device_obj.last_seen = datetime.now(timezone.utc)
                db.commit()

        # Create session
        session_obj = VPNSession(
            user_id=user_id,
            device_id=device_obj.id if device_obj else None,
            session_token=str(uuid.uuid4()),
            protocol=protocol,
            client_ip=client_ip,
            assigned_vpn_ip=assigned_vpn_ip,
            upload_bytes=0,
            download_bytes=0,
            connected_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            is_active=True
        )
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)
        return session_obj

    @staticmethod
    def terminate_session(db: Session, session_id: int) -> bool:
        session_obj = db.query(VPNSession).filter(VPNSession.id == session_id).first()
        if not session_obj:
            raise NotFoundHTTP(f"Session {session_id} not found")

        session_obj.is_active = False
        session_obj.disconnected_at = datetime.now(timezone.utc)
        db.commit()
        return True

    @staticmethod
    def record_traffic(db: Session, session_id: int, upload_delta: int, download_delta: int) -> VPNSession:
        session_obj = db.query(VPNSession).filter(VPNSession.id == session_id).first()
        if not session_obj or not session_obj.is_active:
            raise NotFoundHTTP(f"Active session {session_id} not found")

        session_obj.upload_bytes += upload_delta
        session_obj.download_bytes += download_delta
        session_obj.last_activity = datetime.now(timezone.utc)

        # Update user total used traffic
        user = session_obj.user
        user.used_traffic_bytes += (upload_delta + download_delta)

        # If user quota is exceeded, mark session disconnected
        if user.is_quota_depleted:
            session_obj.is_active = False
            session_obj.disconnected_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(session_obj)
        return session_obj

