from datetime import datetime, timezone
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    
    session_token = Column(String(128), unique=True, index=True, nullable=False)
    protocol = Column(String(32), nullable=False)  # openvpn_tcp, openvpn_udp, wireguard
    client_ip = Column(String(64), nullable=True)
    assigned_vpn_ip = Column(String(64), nullable=True)

    # Traffic Accounting for this session (Bytes)
    upload_bytes = Column(BigInteger, default=0, nullable=False)
    download_bytes = Column(BigInteger, default=0, nullable=False)

    connected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    user = relationship("User", back_populates="sessions")
    device = relationship("Device", back_populates="sessions")

    @property
    def total_bytes(self) -> int:
        return self.upload_bytes + self.download_bytes

    @property
    def duration_seconds(self) -> int:
        end_time = self.disconnected_at or datetime.now(timezone.utc)
        start = self.connected_at
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        return int((end_time - start).total_seconds())

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, proto='{self.protocol}', active={self.is_active})>"

