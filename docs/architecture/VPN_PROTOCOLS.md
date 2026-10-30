# VPN Protocols & Cryptographic Implementation

## 1. Supported Protocols

| Protocol | Transport | Default Port | Cipher Suite | Android Support | Best Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenVPN TCP** | TCP | `8443` | `AES-256-GCM`, TLS 1.3 | Native `VpnService` | Bypassing DPI / Firewalls |
| **OpenVPN UDP** | UDP | `1194` | `AES-256-GCM`, TLS 1.3 | Native `VpnService` | Low-latency streaming |
| **WireGuard** | UDP | `51820` | `ChaCha20-Poly1305`, Curve25519 | Native `com.wireguard.android` | High-speed mobile browsing |

---

## 2. Automated PKI Certificate Generation

RouterLink includes an embedded PKI generator built with Python's `cryptography` library (`app.services.pki_service.PKIService`):
- Automatically initializes on first startup if certificates are not detected in `/data/certs/`.
- Generates 2048-bit RSA Root Certificate Authority (`ca.crt`, `ca.key`) valid for 10 years.
- Issues Server Certificate (`server.crt`, `server.key`) with `serverAuth` Extended Key Usage valid for 5 years.
- Embeds the public Root CA directly inside the generated `.ovpn` client profiles.

---

## 3. Real-Time Accounting Mechanism

Accounting is tracked at both the socket and session levels:
- **Client Heartbeat**: The Android client periodically transmits `upload_delta_bytes` and `download_delta_bytes` via `/api/v1/client/heartbeat`.
- **Accounting Worker**: A background daemon monitors total bytes in the database against each user's `traffic_limit_bytes` and `expires_at`.
- **Enforcement**: If `used_traffic_bytes >= traffic_limit_bytes` or `now() >= expires_at`, the worker immediately sets `is_active = false`, terminates the tunnel, and records the event in `audit_logs`.

