# RouterLink 🚀

[![Language: Persian](https://img.shields.io/badge/Language-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C-green.svg)](README.fa.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![RouterOS](https://img.shields.io/badge/MikroTik-RouterOS_7.10+-red.svg)](https://mikrotik.com)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![Android](https://img.shields.io/badge/Android-Kotlin_+_Compose-3DDC84.svg)](https://developer.android.com)
[![Docker](https://img.shields.io/badge/Docker-Multi--Arch-2496ED.svg)](https://www.docker.com)

**RouterLink** is an enterprise-grade, lightweight, and fully automated VPN management and delivery system specifically engineered to run inside **MikroTik RouterOS 7 Linux Containers**. 

It empowers network administrators to deploy a self-hosted VPN service on their MikroTik router within minutes, control users and bandwidth through a modern **Web Administration Panel**, and offer a seamless, zero-config 1-tap connection experience to users through a native **Android Client Application**.

---

## 📋 Table of Contents
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [MikroTik 1-Click Installation](#-mikrotik-1-click-installation)
- [Web Administration Panel](#-web-administration-panel)
- [Android Client Application](#-android-client-application)
- [Publish to GitHub & Build Pipelines](#-publish-to-github--build-pipelines)
- [Repository Structure](#-repository-structure)
- [Security & Data Persistence](#-security--data-persistence)
- [License](#-license)

---

## 🌟 Key Features

### 🖥️ Native MikroTik RouterOS 7 Container Support
- **1-Click Idempotent Installation**: Automatically configures VETH, dedicated bridge (`bridge-routerlink`), firewall NAT rules, persistent mounts, and container startup via `install.rsc`.
- **Zero Configuration Conflict (Non-destructive)**: Never touches existing router configurations, customer bridges, firewall filters, or routing tables.
- **Ultra-Lightweight Footprint**: Memory usage optimized (<75 MB RAM RSS, <90 MB image size), running on Alpine Linux 3.20 for both `x86_64` (CHR/x86) and `arm64` hardware.
- **Persistent Data Guarantee**: Database, certificates, and runtime configurations reside strictly outside the container on RouterOS persistent disk mounts (`/routerlink/data`).

### 🛡️ Modular Protocol Management (PAL)
- **OpenVPN TCP (Default Port 8443)**: Optimized for anti-censorship and firewall traversal with TLS 1.3 signatures and AES-256-GCM.
- **OpenVPN UDP (Port 1194)**: Low-latency streaming and gaming tunnel.
- **WireGuard (Port 51820)**: High-speed, modern tunnel with Curve25519 cryptography and automated key management.

### 📊 Real-Time Accounting & Quota Enforcement
- **Precise Bandwidth Accounting**: Tracks upload and download volume per user.
- **Strict Limit Enforcement**: Background worker terminates active sessions when traffic quota is reached or subscription expires.
- **Concurrent Connection Control**: Limits simultaneous device connections per user account.
- **Persistent Sessions**: State is retained across container restarts or router reboots.

### 💻 Modern Web Administration Panel
- **Responsive Dashboard**: Real-time CPU, RAM, Disk, active connections, and bandwidth throughput charts.
- **User Management**: Full CRUD, expiration dates, custom quotas, protocol permissions, and QR code provisioning.
- **Protocol & Certificate Hub**: Change listening ports, inspect daemon logs, restart services, and manage PKI certificates.
- **Active Session Terminal**: View active connections with remote IP, duration, speed, and 1-click disconnect.
- **Backup & Restore**: Export/import database and configuration archives directly from the browser.

### 📱 Native Android Client
- **Zero-Config 1-Tap Connect**: Syncs VPN configuration and protocol profiles via QR scan or credentials.
- **Real VPN Tunnel**: Built on Android's native `VpnService` with OpenVPN and WireGuard engines (no fake status).
- **Live Diagnostics**: Speedometer, data usage counter, ping latency test, and tunnel logs.
- **Auto-Reconnection**: Seamlessly switches between Wi-Fi and mobile data networks.

---

## 🏗️ System Architecture

```text
                  ADMINISTRATOR
                        │
                        ▼ Browser (Port 8080)
              RouterLink Web Administration Panel
                        │
                        ▼
       RouterLink Backend (FastAPI + SQLite WAL)
       ┌────────────────┬────────────────┐
       ▼                ▼                ▼
 User Management  Protocol Engine  Traffic Accounting
       │                │                │
       └────────────────┼────────────────┘
                        ▼
              VPN Daemons (tun0 / wg0)
                        │
                        ▼
             MikroTik RouterOS 7 Host
             (VETH / NAT / Persistent Storage)
                        │
                        ▼ Internet
                        ▲
                        │
           RouterLink Android Client
           (Kotlin + Jetpack + VpnService)
```

For full architectural specifications, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🚀 MikroTik 1-Click Installation

Connect to your MikroTik router via Terminal / WinBox and run:

```routeros
# Download and execute the automated installer
/tool fetch url="https://raw.githubusercontent.com/<YOUR-GITHUB-USERNAME>/RouterLink/main/mikrotik/install.rsc" dst-path="install.rsc"
/import install.rsc
```

### What the installer automates:
1. Verifies RouterOS version (>= 7.10) and container package installation.
2. Creates isolated virtual ethernet (`veth-routerlink` with `172.28.0.2/24`).
3. Creates dedicated bridge (`bridge-routerlink` with gateway `172.28.0.1/24`).
4. Configures persistent mount (`/routerlink/data` -> `/data`).
5. Configures labeled NAT port-forwards for 8080 (Web), 8443 (OpenVPN TCP), 1194 (OpenVPN UDP), and 51820 (WireGuard).
6. Pulls the multi-arch container from GitHub Container Registry and starts the service.
7. Prints WebUI access URL (`http://<router-ip>:8080`).

---

## 💻 Web Administration Panel

1. Open `http://<your-router-ip>:8080` in your browser.
2. Complete the initial setup wizard:
   - Configure Master Administrator credentials.
   - Set public server IP or DDNS hostname.
3. Access the dashboard:
   - **Users**: Add users, set quota (GB) and expiry date.
   - **QR Code**: Generate 1-click Android setup barcode.
   - **Live Sessions**: Inspect active VPN tunnels and terminate sessions on demand.
   - **Protocols**: Toggle OpenVPN and WireGuard ports and inspect real-time logs.
   - **Backup**: Download or restore SQLite database snapshots.

---

## 📱 Android Client Application

### Download APK
The pre-compiled release APK (`RouterLink-Release.apk`) is automatically built by GitHub Actions and available on the **Releases** page of this repository.

### Connecting to Server:
1. Install `RouterLink-Release.apk` on your Android device (Android 8.0+).
2. Tap **Scan Setup QR Code** and scan the QR code generated in the WebUI.
3. Select your protocol (e.g. **OpenVPN TCP 8443** or **WireGuard**).
4. Tap **CONNECT** and approve the standard Android VPN permission.
5. Live transfer speed, remaining quota, and duration will be displayed in real time.

---

## 🚀 Publish to GitHub & Build Pipelines

RouterLink is configured with complete GitHub Actions CI/CD workflows:
- **Multi-Arch Docker Build (`docker-build.yml`)**: Compiles and pushes `linux/amd64` and `linux/arm64` images to GitHub Container Registry (`ghcr.io`).
- **Android APK Build (`android-build.yml`)**: Compiles `RouterLink-Release.apk` and `RouterLink-Debug.apk`.
- **Release Automation (`release.yml`)**: When a tag (e.g. `v1.0.0`) is pushed, creates a GitHub Release with the compiled Android APK and MikroTik script bundle.

### Option 1: Automated Script (Fastest)

#### Windows (PowerShell):
```powershell
.\scripts\publish_to_github.ps1 "https://github.com/<YOUR-USERNAME>/RouterLink.git"
```

#### Linux / macOS (Bash):
```bash
chmod +x scripts/publish_to_github.sh
./scripts/publish_to_github.sh "https://github.com/<YOUR-USERNAME>/RouterLink.git"
```

---

### Option 2: Step-by-Step Manual Git Commands

```bash
# 1. Initialize local repository
git init -b main

# 2. Stage all files (.gitignore excludes runtime artifacts)
git add .

# 3. Create initial commit
git commit -m "feat: initial production release of RouterLink v1.0.0"

# 4. Link your GitHub repository
git remote add origin https://github.com/<YOUR-USERNAME>/RouterLink.git

# 5. Push main branch (triggers Docker and Android APK builds)
git push -u origin main

# 6. Create release tag and push (triggers GitHub Release creation)
git tag -a v1.0.0 -m "RouterLink v1.0.0 Release"
git push origin v1.0.0
```

---

## 📂 Repository Structure

```text
RouterLink/
├── server/
│   ├── backend/             # FastAPI REST & WebSocket server
│   │   ├── app/             # Application source (API, Core, Models, Services)
│   │   ├── static/          # Embedded production-ready WebUI
│   │   ├── alembic/         # Database migrations
│   │   ├── requirements.txt # Python dependencies
│   │   └── pyproject.toml   # Project metadata
│   └── webui/               # React + TypeScript + Tailwind source
├── android/                 # Native Android Client application
│   ├── app/                 # Kotlin Android app module (VpnService, Jetpack Compose)
│   ├── gradle/              # Gradle wrapper
│   └── build.gradle.kts     # Build configuration
├── mikrotik/                # RouterOS 7 Automation Scripts
│   ├── install.rsc          # Non-destructive 1-Click installation script
│   ├── update.rsc           # Safe in-place update script
│   ├── uninstall.rsc        # Clean teardown script
│   ├── backup.rsc           # Database & config backup
│   └── restore.rsc          # Database & config restore
├── deployment/
│   └── docker/              # Alpine 3.20 multi-arch Dockerfile & entrypoint
├── scripts/                 # GitHub publisher scripts (ps1 & sh)
├── .github/workflows/       # GitHub Actions CI/CD workflows
├── docs/                    # Technical & REST API documentation
├── tests/                   # Backend & MikroTik test suites
├── ARCHITECTURE.md          # Detailed architecture specification
├── DEVELOPMENT_PLAN.md      # Roadmap & development plan
├── README.md                # English documentation (this file)
├── README.fa.md             # Persian documentation
└── LICENSE                  # Apache 2.0 License
```

---

## 🔒 Security & Data Persistence

- **Zero Data Loss**: Database records, encryption keys, and configuration files are stored outside the container inside `/routerlink/data`.
- **Modern Cryptography**: Passwords hashed with `bcrypt`. Admin sessions protected with cryptographically signed JWTs.
- **Isolated Network Namespace**: Container executes with restricted Linux capabilities (`NET_ADMIN`, `NET_RAW`) in its own VETH network.

---

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
