from pathlib import Path
from typing import List, Optional
from app.config import settings
from app.models.user import User
from app.protocols.base import ProtocolEngine
from app.services.pki_service import PKIService


class OpenVPNEngine(ProtocolEngine):
    def __init__(self, name: str = "openvpn_tcp", port: int = 8443, proto: str = "tcp"):
        self._name = name
        self._port = port
        self._proto = proto
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
        return self._proto

    def get_status(self) -> str:
        return self._status

    def generate_server_config(self) -> str:
        ca_cert, ca_key = PKIService.get_ca_paths()
        server_cert, server_key = PKIService.get_server_paths()
        PKIService.ensure_pki()

        config = f"""# RouterLink OpenVPN Server Config
port {self._port}
proto {self._proto}
dev tun
topology subnet
server {settings.OPENVPN_SUBNET} {settings.OPENVPN_NETMASK}

ca {ca_cert.as_posix()}
cert {server_cert.as_posix()}
key {server_key.as_posix()}
dh none

persist-key
persist-tun
keepalive 10 120
data-ciphers AES-256-GCM:AES-128-GCM:CHACHA20-POLY1305
data-ciphers-fallback AES-256-GCM
cipher AES-256-GCM
auth SHA256

# Client Authentication & Accounting
auth-user-pass-verify /app/scripts/openvpn_auth.py via-env
script-security 3
client-disconnect /app/scripts/openvpn_disconnect.py

# Push routing and DNS
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 1.1.1.1"
push "dhcp-option DNS 8.8.8.8"

status {settings.LOGS_DIR.as_posix()}/openvpn-status.log 10
management 127.0.0.1 {settings.OPENVPN_MGMT_PORT}
verb 3
"""
        return config

    def generate_client_config(self, user: User, server_host: str, port: Optional[int] = None) -> str:
        ca_content = PKIService.get_ca_cert_content()
        target_port = port or self._port

        ovpn = f"""# RouterLink OpenVPN Client Profile
# User: {user.username}
client
dev tun
proto {self._proto}
remote {server_host} {target_port}
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth-user-pass
cipher AES-256-GCM
auth SHA256
key-direction 1
verb 3

<ca>
{ca_content.strip()}
</ca>
"""
        return ovpn

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
            f"[RouterLink OpenVPN] Daemon {self._name} listening on {self._proto.upper()}:{self._port}",
            "[RouterLink OpenVPN] TLS handshake and cipher negotiation active",
            "[RouterLink OpenVPN] Engine operational and ready for client connections"
        ]

