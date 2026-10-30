from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ProtocolConfigResponse(BaseModel):
    id: int
    protocol_name: str
    is_enabled: bool
    listen_port: int
    transport_type: str
    cipher_settings: Optional[str]
    status: str = "running" # running, stopped, error
    connected_clients: int = 0

    model_config = ConfigDict(from_attributes=True)


class ProtocolUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    listen_port: Optional[int] = Field(None, ge=1, le=65535)
    cipher_settings: Optional[str] = None


class ProtocolActionRequest(BaseModel):
    action: str = Field(..., pattern="^(start|stop|restart)$")


class ProtocolLogResponse(BaseModel):
    protocol_name: str
    lines: List[str]
