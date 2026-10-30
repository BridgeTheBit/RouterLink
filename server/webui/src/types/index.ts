export interface User {
  id: number;
  username: string;
  email?: string;
  is_active: boolean;
  traffic_limit_bytes: number;
  used_traffic_bytes: number;
  remaining_traffic_bytes?: number;
  is_expired: boolean;
  is_quota_depleted: boolean;
  can_connect: boolean;
  subscription_start: string;
  expires_at?: string;
  max_concurrent_connections: number;
  max_registered_devices: number;
  allowed_protocols: string;
  created_at: string;
  updated_at: string;
  active_sessions_count: number;
}

export interface ProtocolConfig {
  id: number;
  protocol_name: string;
  is_enabled: boolean;
  listen_port: number;
  transport_type: string;
  cipher_settings?: string;
  status: string;
  connected_clients: number;
}

export interface Session {
  id: number;
  user_id: number;
  username?: string;
  device_name?: string;
  protocol: string;
  client_ip?: string;
  assigned_vpn_ip?: string;
  upload_bytes: number;
  download_bytes: number;
  total_bytes: number;
  duration_seconds: number;
  connected_at: string;
  is_active: boolean;
}

export interface SystemStats {
  cpu_percent: number;
  ram_total_mb: number;
  ram_used_mb: number;
  ram_percent: number;
  disk_total_gb: number;
  disk_used_gb: number;
  disk_percent: number;
  uptime_seconds: number;
  total_users: number;
  online_users: number;
  active_sessions: number;
  total_upload_bytes: number;
  total_download_bytes: number;
  total_traffic_bytes: number;
}

export interface BackupInfo {
  filename: string;
  size_bytes: number;
  created_at: string;
}

export interface AuditLog {
  id: number;
  actor_type: string;
  actor_id?: string;
  action: string;
  target_entity?: string;
  ip_address?: string;
  created_at: string;
}

