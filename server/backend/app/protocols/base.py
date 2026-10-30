from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.user import User


class ProtocolEngine(ABC):
    """Abstract interface for all VPN protocol engines."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Protocol unique identifier (e.g. 'openvpn_tcp', 'wireguard')."""
        pass

    @property
    @abstractmethod
    def default_port(self) -> int:
        pass

    @property
    @abstractmethod
    def transport(self) -> str:
        """tcp or udp"""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Returns 'running', 'stopped', or 'error'."""
        pass

    @abstractmethod
    def generate_client_config(self, user: User, server_host: str, port: Optional[int] = None) -> str:
        """Generates ready-to-import client configuration profile content."""
        pass

    @abstractmethod
    def start(self) -> bool:
        pass

    @abstractmethod
    def stop(self) -> bool:
        pass

    @abstractmethod
    def restart(self) -> bool:
        pass

    @abstractmethod
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        pass

