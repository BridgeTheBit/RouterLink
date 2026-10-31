from pathlib import Path
from typing import List, Optional
from app.config import settings
from app.models.user import User
from app.protocols.base import ProtocolEngine


class IkeV2Engine(ProtocolEngine):
    """IKEv2/IPSec VPN protocol engine (strongSwan-based configuration)."""

    def __init__(self, name: str = "ikev2", port: int = 500):
        self._name = name
        self._port = port
        self._status = "running"
        self._log_file = settings.LOGS_DIR / f"{self._name}.log"

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_port(self) -> int:
        return self._port

    @property
    def transport(self) -> str:
        return "udp"

    def get_status(self) -> str:
        return self._status

    def generate_client_config(self, user: User, server_host: str, port: Optional[int] = None) -> str:
        """Returns a strongSwan-compatible .sswan profile as a JSON string."""
        target_port = port or self._port
        import json
        profile = {
            "uuid": f"rl-{user.id:04d}-ikev2",
            "name": f"RouterLink-{user.username}",
            "type": "ikev2-eap",
            "remote": {
                "addr": server_host,
                "port": str(target_port),
            },
            "local": {
                "eap_id": user.username,
            },
            "eap": {
                "eap_id": user.username,
                "password": "__USER_VPN_PASSWORD__",
            },
            "split-tunneling": [
                {
                    "type": "include",
                    "subnets": ["0.0.0.0/0"],
                }
            ],
        }
        return json.dumps(profile, indent=2, ensure_ascii=False)

    def start(self) -> bool:
        self._status = "running"
        return True

    def stop(self) -> bool:
        self._status = "stopped"
        return True

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def get_recent_logs(self, lines: int = 50) -> List[str]:
        if self._log_file.exists():
            try:
                all_lines = self._log_file.read_text(encoding="utf-8").splitlines()
                return all_lines[-lines:]
            except Exception:
                pass
        return [f"[{self._name}] No log file found."]

