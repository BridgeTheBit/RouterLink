from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class SystemStats(BaseModel):
    cpu_percent: float
    ram_total_mb: float
    ram_used_mb: float
    ram_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    uptime_seconds: int
    total_users: int
    online_users: int
    active_sessions: int
    total_upload_bytes: int
    total_download_bytes: int
    total_traffic_bytes: int


class AuditLogResponse(BaseModel):
    id: int
    actor_type: str
    actor_id: Optional[str]
    action: str
    target_entity: Optional[str]
    ip_address: Optional[str]
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class BackupInfo(BaseModel):
    filename: str
    size_bytes: int
    created_at: str
