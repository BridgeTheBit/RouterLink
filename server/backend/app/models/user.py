from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Traffic Accounting (Bytes) - 0 or NULL means unlimited
    traffic_limit_bytes = Column(BigInteger, default=0, nullable=False)  # 0 = unlimited
    used_traffic_bytes = Column(BigInteger, default=0, nullable=False)

    # Subscription Validity - NULL means lifetime/unlimited
    subscription_start = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Concurrency and Device Limits
    max_concurrent_connections = Column(Integer, default=1, nullable=False)
    max_registered_devices = Column(Integer, default=5, nullable=False)

    # Allowed Protocols: Comma-separated list (e.g. "openvpn_tcp,openvpn_udp,wireguard")
    allowed_protocols = Column(String(255), default="openvpn_tcp,wireguard", nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    @property
    def remaining_traffic_bytes(self) -> Optional[int]:
        if self.traffic_limit_bytes == 0:
            return None  # Unlimited
        remaining = self.traffic_limit_bytes - self.used_traffic_bytes
        return max(0, remaining)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc if self.expires_at.tzinfo is None else None)

    @property
    def is_quota_depleted(self) -> bool:
        if self.traffic_limit_bytes == 0:
            return False
        return self.used_traffic_bytes >= self.traffic_limit_bytes

    @property
    def can_connect(self) -> bool:
        return self.is_active and not self.is_expired and not self.is_quota_depleted

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', active={self.is_active})>"

