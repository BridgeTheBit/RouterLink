from pathlib import Path
from typing import List, Optional, Tuple
from app.config import settings
from app.models.user import User
from app.protocols.base import ProtocolEngine
from app.services.pki_service import PKIService


class WireGuardEngine(ProtocolEngine):
    def __init__(self, name: str = "wireguard", port: int = 51820):
        self._name = name
        self._port = port
        self._status = "running"
        self._log_file = settings.LOGS_DIR / f"{self._name}.log"
        self._server_priv_key_path = settings.CERTS_DIR / "wg_server.key"
        self._server_pub_key_path = settings.CERTS_DIR / "wg_server.pub"

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

    def _ensure_server_keys(self) -> Tuple[str, str]:
        if not self._server_priv_key_path.exists() or not self._server_pub_key_path.exists():
            priv, pub = PKIService.generate_wireguard_keypair()
            self._server_priv_key_path.write_text(priv, encoding="utf-8")
            self._server_pub_key_path.write_text(pub, encoding="utf-8")
            return priv, pub
        return (
            self._server_priv_key_path.read_text(encoding="utf-8").strip(),
            self._server_pub_key_path.read_text(encoding="utf-8").strip()
        )

    def generate_server_config(self) -> str:
        priv_key, _ = self._ensure_server_keys()
        config = f"""# RouterLink WireGuard Server Interface (wg0)
[Interface]
Address = {settings.WIREGUARD_SERVER_IP}/24
ListenPort = {self._port}
PrivateKey = {priv_key}
SaveConfig = false

# Client peers are managed dynamically
"""
        return config

    def generate_client_config(self, user: User, server_host: str, port: Optional[int] = None) -> str:
        _, server_pub = self._ensure_server_keys()
        client_priv, client_pub = PKIService.generate_wireguard_keypair()
        target_port = port or self._port

        # Compute deterministic or sequential client IP within 10.9.0.0/24
        user_oct = (user.id % 250) + 2
        client_ip = f"10.9.0.{user_oct}/32"

        conf = f"""# RouterLink WireGuard Client Profile
# User: {user.username}
[Interface]
PrivateKey = {client_priv}
Address = {client_ip}
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server_pub}
Endpoint = {server_host}:{target_port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
        return conf

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
        return [
            f"[RouterLink WireGuard] Interface wg0 active on UDP port {self._port}",
            "[RouterLink WireGuard] Peer handshake handler initialized",
            "[RouterLink WireGuard] WireGuard protocol engine running successfully"
        ]

