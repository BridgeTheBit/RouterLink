from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    device_name: Optional[str] = None
    protocol: str
    client_ip: Optional[str]
    assigned_vpn_ip: Optional[str]
    upload_bytes: int
    download_bytes: int
    total_bytes: int
    duration_seconds: int
    connected_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DisconnectResponse(BaseModel):
    success: bool
    message: str
    session_id: int
