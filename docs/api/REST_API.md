# RouterLink REST API Documentation

Base URI: `/api/v1`

All responses are formatted in JSON unless fetching configuration profiles.

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### Check Setup Status
- **Method**: `GET`
- **Path**: `/api/v1/auth/setup/status`
- **Response**:
```json
{
  "is_setup_required": false,
  "app_name": "RouterLink",
  "app_version": "1.0.0"
}
```

### Initial SuperAdmin Setup
- **Method**: `POST`
- **Path**: `/api/v1/auth/setup`
- **Body**:
```json
{
  "username": "admin",
  "password": "SuperAdminPassword123!",
  "confirm_password": "SuperAdminPassword123!"
}
```
- **Response**: Token response with `access_token` and `role: "superadmin"`.

### Administrator Login
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Body**:
```json
{
  "username": "admin",
  "password": "SuperAdminPassword123!"
}
```
- **Response**:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "role": "superadmin",
  "username": "admin",
  "expires_in": 604800
}
```

---

## 2. Administrator User Management (`/api/v1/admin/users`)
*Requires `Authorization: Bearer <token>` with `superadmin` or `admin` role.*

### List Users
- **Method**: `GET`
- **Query Params**: `skip` (default 0), `limit` (default 100), `search` (optional)

### Create User
- **Method**: `POST`
- **Body**:
```json
{
  "username": "alice",
  "password": "AlicePassword123!",
  "email": "alice@example.com",
  "traffic_limit_bytes": 10737418240,
  "expires_at": "2026-12-31T23:59:59Z",
  "max_concurrent_connections": 2,
  "max_registered_devices": 3,
  "allowed_protocols": "openvpn_tcp,wireguard"
}
```

### Update Quota
- **Method**: `POST`
- **Path**: `/api/v1/admin/users/{user_id}/quota`
- **Body**:
```json
{
  "additional_traffic_bytes": 5368709120,
  "reset_used_traffic": false
}
```

---

## 3. Protocol Management (`/api/v1/admin/protocols`)

### List Protocols
- **Method**: `GET`
- **Response**: List of active engines (`openvpn_tcp`, `openvpn_udp`, `wireguard`), listening ports, ciphers, and live connected clients.

### Protocol Control Action
- **Method**: `POST`
- **Path**: `/api/v1/admin/protocols/{name}/action`
- **Body**: `{"action": "restart"}` (or `start` / `stop`)

---

## 4. Session & Real-time Management (`/api/v1/admin/sessions`)

### List Active Sessions
- **Method**: `GET`
- **Query Params**: `active_only=true`

### Terminate / Kill Session
- **Method**: `POST`
- **Path**: `/api/v1/admin/sessions/{session_id}/terminate`

---

## 5. Mobile Client API (`/api/v1/client`)

### Client Login
- **Method**: `POST`
- **Path**: `/api/v1/client/login`
- **Body**: `{"username": "alice", "password": "AlicePassword123!"}`

### Fetch Profile & Remaining Quota
- **Method**: `GET`
- **Path**: `/api/v1/client/profile`
- **Headers**: `Authorization: Bearer <client_token>`

### Download OpenVPN Profile
- **Method**: `GET`
- **Path**: `/api/v1/client/config/openvpn?proto=tcp`
- **Response**: Ready-to-import `.ovpn` configuration file embedding `<ca>`.

### Download WireGuard Profile
- **Method**: `GET`
- **Path**: `/api/v1/client/config/wireguard`
- **Response**: Ready-to-import `.conf` WireGuard configuration file.

### Client Heartbeat & Accounting Sync
- **Method**: `POST`
- **Path**: `/api/v1/client/heartbeat`
- **Body**:
```json
{
  "session_token": "uuid-here",
  "device_id": "phone-uuid",
  "protocol": "openvpn_tcp",
  "upload_delta_bytes": 245000,
  "download_delta_bytes": 1048576
}
```

