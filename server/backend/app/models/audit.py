from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_type = Column(String(32), default="admin", nullable=False) # admin, client, system
    actor_id = Column(String(64), nullable=True)
    action = Column(String(64), nullable=False) # e.g. USER_CREATE, PROTOCOL_RESTART, QUOTA_DEPLETED
    target_entity = Column(String(64), nullable=True) # e.g. user:john, protocol:openvpn_tcp
    ip_address = Column(String(64), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog(action='{self.action}', target='{self.target_entity}', actor='{self.actor_id}')>"

