from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: Optional[EmailStr] = None
    is_active: bool = True
    traffic_limit_bytes: int = Field(default=0, ge=0) # 0 = Unlimited
    expires_at: Optional[datetime] = None
    max_concurrent_connections: int = Field(default=1, ge=1, le=20)
    max_registered_devices: int = Field(default=5, ge=1, le=50)
    allowed_protocols: str = "openvpn_tcp,wireguard"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    traffic_limit_bytes: Optional[int] = Field(None, ge=0)
    expires_at: Optional[datetime] = None
    max_concurrent_connections: Optional[int] = Field(None, ge=1, le=20)
    max_registered_devices: Optional[int] = Field(None, ge=1, le=50)
    allowed_protocols: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=128)


class UserResponse(UserBase):
    id: int
    used_traffic_bytes: int
    remaining_traffic_bytes: Optional[int]
    is_expired: bool
    is_quota_depleted: bool
    can_connect: bool
    subscription_start: datetime
    created_at: datetime
    updated_at: datetime
    active_sessions_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserQuotaUpdate(BaseModel):
    additional_traffic_bytes: Optional[int] = Field(0, ge=0)
    new_traffic_limit_bytes: Optional[int] = Field(None, ge=0)
    reset_used_traffic: bool = False
    new_expires_at: Optional[datetime] = None
