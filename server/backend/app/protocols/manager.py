from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models.protocol import ProtocolConfig
from app.protocols.base import ProtocolEngine
from app.protocols.openvpn import OpenVPNEngine
from app.protocols.wireguard import WireGuardEngine


class ProtocolManager:
    def __init__(self):
        self._engines: Dict[str, ProtocolEngine] = {
            "openvpn_tcp": OpenVPNEngine(name="openvpn_tcp", port=settings.OPENVPN_PORT, proto="tcp"),
            "openvpn_udp": OpenVPNEngine(name="openvpn_udp", port=1194, proto="udp"),
            "wireguard": WireGuardEngine(name="wireguard", port=settings.WIREGUARD_PORT),
        }

    def get_engine(self, name: str) -> Optional[ProtocolEngine]:
        return self._engines.get(name)

    def list_engines(self) -> List[ProtocolEngine]:
        return list(self._engines.values())

    def initialize_defaults(self, db: Session) -> None:
        """Seed default protocol configuration records if not present in DB."""
        for engine in self._engines.values():
            existing = db.query(ProtocolConfig).filter(ProtocolConfig.protocol_name == engine.name).first()
            if not existing:
                cfg = ProtocolConfig(
                    protocol_name=engine.name,
                    is_enabled=True,
                    listen_port=engine.default_port,
                    transport_type=engine.transport,
                    cipher_settings="AES-256-GCM" if "openvpn" in engine.name else "ChaCha20-Poly1305"
                )
                db.add(cfg)
        db.commit()


protocol_manager = ProtocolManager()

