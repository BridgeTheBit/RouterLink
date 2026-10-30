from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.db.base import Base


class ProtocolConfig(Base):
    __tablename__ = "protocol_configs"

    id = Column(Integer, primary_key=True, index=True)
    protocol_name = Column(String(32), unique=True, index=True, nullable=False) # openvpn_tcp, openvpn_udp, wireguard
    is_enabled = Column(Boolean, default=True, nullable=False)
    listen_port = Column(Integer, nullable=False)
    transport_type = Column(String(16), nullable=False) # tcp or udp
    cipher_settings = Column(String(255), default="AES-256-GCM:CHACHA20-POLY1305", nullable=True)
    raw_config_template = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<ProtocolConfig(protocol='{self.protocol_name}', port={self.listen_port}, enabled={self.is_enabled})>"

