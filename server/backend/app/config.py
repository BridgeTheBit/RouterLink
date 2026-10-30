import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    APP_NAME: str = "RouterLink"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8080

    # Data & Persistence Paths
    DATA_DIR: Path = Path(os.environ.get("ROUTERLINK_DATA_DIR", "d:/Mehran/Mikrolink/data" if os.name == "nt" else "/data"))
    
    @property
    def DB_PATH(self) -> Path:
        db_dir = self.DATA_DIR / "db"
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / "routerlink.db"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"sqlite:///{self.DB_PATH.as_posix()}"

    @property
    def CERTS_DIR(self) -> Path:
        certs = self.DATA_DIR / "certs"
        certs.mkdir(parents=True, exist_ok=True)
        return certs

    @property
    def CONFIG_DIR(self) -> Path:
        cfg = self.DATA_DIR / "config"
        cfg.mkdir(parents=True, exist_ok=True)
        return cfg

    @property
    def LOGS_DIR(self) -> Path:
        logs = self.DATA_DIR / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        return logs

    # Security & Tokens
    SECRET_KEY: str = os.environ.get("ROUTERLINK_SECRET_KEY", "super-secret-routerlink-development-key-change-in-prod-32bytes")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    CLIENT_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days

    # Protocol Defaults
    OPENVPN_PORT: int = 8443
    OPENVPN_PROTO: str = "tcp"
    OPENVPN_SUBNET: str = "10.8.0.0"
    OPENVPN_NETMASK: str = "255.255.255.0"
    OPENVPN_MGMT_PORT: int = 7505

    WIREGUARD_PORT: int = 51820
    WIREGUARD_SUBNET: str = "10.9.0.0/24"
    WIREGUARD_SERVER_IP: str = "10.9.0.1"

    # MikroTik Network Information
    VETH_CONTAINER_IP: str = "172.28.0.2"
    VETH_GATEWAY_IP: str = "172.28.0.1"
    SERVER_PUBLIC_HOST: str = "127.0.0.1"  # Or router DDNS / public IP

    # Background Accounting Frequency (seconds)
    ACCOUNTING_INTERVAL_SECONDS: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_prefix="ROUTERLINK_",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

