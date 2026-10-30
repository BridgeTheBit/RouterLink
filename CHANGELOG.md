# Changelog

All notable changes to the **RouterLink** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Phase 7 (Integration, Documentation & CI/CD Pipelines)**:
  - CI/CD workflows: `backend-ci.yml`, `docker-build.yml` (multi-arch), `android-build.yml` (APK packaging), and `release.yml`.
  - Comprehensive documentation in `docs/api/REST_API.md`, `docs/architecture/MIKROTIK_CONTAINER.md`, `docs/architecture/VPN_PROTOCOLS.md`.
- **Phase 6 (Android Client Application)**:
  - Native Kotlin + Jetpack Compose + Material 3 client in `android/`.
  - Gradle Kotlin DSL build setup (`build.gradle.kts`, `app/build.gradle.kts`, `gradle-wrapper.properties`).
  - Native `RouterLinkVpnService` with real TUN descriptor (`10.8.0.2/24`, `0.0.0.0/0`, DNS), real-time byte counters, and foreground notification.
  - Periodic heartbeat worker syncing traffic delta and enforcing remote quota/subscription expiration cutoff.
  - Automatic reconnection upon Wi-Fi / Cellular network switching via `ConnectivityManager.NetworkCallback`.
  - Screens: `HomeScreen` (1-tap Connect, speedometer, quota progress), `LoginScreen` (QR code scanner, server URL), `ProtocolsScreen`, and `DiagnosticsScreen`.
  - Unit tests in `android/app/src/test/java/com/routerlink/app/RouterLinkUnitTest.kt`.
- **Phase 5 (MikroTik RouterOS 7 Automation)**:
  - 1-Click idempotent, safe installer `mikrotik/install.rsc` for RouterOS 7 (VETH, bridge, NAT, persistent mount, container run).
  - Safe in-place update script `mikrotik/update.rsc` preserving `/routerlink/data`.
  - Non-destructive teardown script `mikrotik/uninstall.rsc` safely removing only RouterLink-labeled rules.
  - Backup & restore automation scripts `mikrotik/backup.rsc` and `mikrotik/restore.rsc`.
  - Automated test suite `tests/mikrotik/test_rsc_scripts.py` verifying rule idempotency and safety.
- **Phase 4 (Containerization & Deployment)**:
  - Multi-arch Dockerfile (`deployment/docker/Dockerfile`) optimized on Alpine Linux 3.20 (< 90 MB total size).
  - Production container entrypoint script `deployment/docker/entrypoint.sh` with persistent storage wiring, TUN device initialization, Alembic auto-migration, and daemon management.
  - Docker Compose staging environment `deployment/docker/docker-compose.yml`.
- **Phase 3 (Web Administration Panel)**:
  - Single-Page Application (SPA) administration interface embedded inside server (`server/backend/static`).
  - First-Run Setup Wizard view for master administrator account initialization.
  - Live Dashboard view with real-time gauges (CPU, RAM, Disk, Uptime), active user/session counters, and live SVG throughput waveform monitor.
  - User & Quota Management view with search, filter, Add/Edit User modal, traffic quota limits, expiration dates, protocol checkboxes, and Android setup QR Code generator.
  - Protocol Management view with real-time service health badges, port changer, toggle switch, daemon restart action, and live log viewer modal.
  - Active Session Explorer with remote client IPs, duration timer, upload/download counters, and 1-click "Kill / Terminate" button.
  - System Settings & Maintenance view with SQLite database backup creator, download links, and security audit log table.
  - Automated integration test `test_webui_static_serving` verifying seamless SPA routing and static asset delivery.
- **Phase 2 (Backend & Database Engine)**:
  - Complete FastAPI REST & WebSocket server structure.
  - SQLite with WAL mode, foreign keys, and Alembic versioned migrations.
  - SQLAlchemy ORM models: `AdminUser`, `User`, `Device`, `Session`, `ProtocolConfig`, `AuditLog`.
  - Self-contained PKI cryptographic engine for X.509 CA/Server certs and WireGuard Curve25519 keypairs.
  - Protocol Abstraction Layer (PAL) with `OpenVPNEngine` (TCP/UDP, `.ovpn` generator) and `WireGuardEngine` (`.conf` generator).
  - Background `AccountingWorker` daemon enforcing real-time quotas, expiration dates, and concurrent connection caps.
  - Comprehensive Admin API (`/api/v1/admin/users`, `/protocols`, `/sessions`, `/system`).
  - Mobile Client API (`/api/v1/client/login`, `/profile`, `/config/openvpn`, `/config/wireguard`, `/heartbeat`).
  - 100% passing automated test suite with pytest.
- **Phase 1 (Architecture & Foundation)**:
  - Initial project architecture and technical specifications (`ARCHITECTURE.md`).
  - Multi-phase engineering roadmap and acceptance criteria (`DEVELOPMENT_PLAN.md`).
  - Root `README.md`, `LICENSE` (Apache-2.0), `CONTRIBUTING.md`, and `SECURITY.md`.
  - Foundational repository structure.

