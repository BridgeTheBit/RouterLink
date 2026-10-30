# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Security is paramount in RouterLink. If you discover a potential security vulnerability in RouterLink Server, WebUI, Android Client, or MikroTik scripts:

1. **Do not disclose the vulnerability publicly.**
2. Send an email to `security@routerlink.io` (or report via private GitHub Security Advisory).
3. Include detailed reproduction steps, proof of concept, affected versions, and potential impact.
4. We acknowledge receipt within 48 hours and aim to provide a security patch within 7 days.

## Security Architecture Principles
- **No Hardcoded Secrets**: All sensitive keys, tokens, and certificates are generated dynamically and stored in `/data`.
- **Minimal Privileges**: Container executes with restricted Linux capabilities (`NET_ADMIN`, `NET_RAW`).
- **Cryptographic Standards**: `argon2id` / `bcrypt` for passwords, TLS 1.3 / ChaCha20-Poly1305 / AES-256-GCM for tunnels.
- **Host Isolation**: Traffic isolation between the container subnet (`172.28.0.0/24`) and private LANs via RouterOS firewall rules.

