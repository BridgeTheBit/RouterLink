# MikroTik RouterOS 7 Container Architecture Deep Dive

## 1. Overview

RouterOS 7 introduces a native Linux container runtime compatible with OCI/Docker images. RouterLink runs inside this runtime to avoid interfering with RouterOS core services while offering high flexibility, modern Python 3, and rich cryptographic capabilities.

---

## 2. Network Topology & VETH

```text
               MikroTik RouterOS 7 Host
               ┌────────────────────────────────────────────────────────┐
               │                                                        │
WAN Interface ─┼─► [/ip firewall nat]                                   │
               │   ├── dst-nat :8080   ─► 172.28.0.2:8080 (WebUI/API)   │
               │   ├── dst-nat :8443   ─► 172.28.0.2:8443 (OpenVPN TCP) │
               │   ├── dst-nat :51820  ─► 172.28.0.2:51820 (WireGuard)  │
               │   └── src-nat masq    ◄─ 172.28.0.0/24 (Outbound)      │
               │                                                        │
               │   [bridge-routerlink] (172.28.0.1/24)                  │
               │            ▲                                           │
               │            │                                           │
               │   [veth-routerlink] (172.28.0.2/24)                    │
               │            ▲                                           │
               └────────────┼───────────────────────────────────────────┘
                            │
               ┌────────────▼───────────────────────────────────────────┐
               │ RouterLink Linux Container (Alpine 3.20)               │
               │   ├── eth0: 172.28.0.2/24, Gateway: 172.28.0.1        │
               │   ├── tun0: 10.8.0.1/24 (OpenVPN Virtual Subnet)       │
               │   ├── wg0:  10.9.0.1/24 (WireGuard Virtual Subnet)     │
               │   └── /data ◄── mounted from /routerlink/data on host │
               └────────────────────────────────────────────────────────┘
```

---

## 3. Persistent Storage Guarantees

In RouterOS, container root filesystems are ephemeral. Any file written to container root (`/`, `/tmp`, etc.) will be purged when the container is deleted or updated.

RouterLink enforces strict persistence:
- Storage Mount: `/routerlink/data` on host mapped to `/data` in container.
- Database: `/data/db/routerlink.db` (SQLite in WAL mode).
- Keys & Certificates: `/data/certs/` (PKI CA, Server certs, WireGuard keys).
- Logs: `/data/logs/` (Daemon logs).
- Backups: `/data/backups/`.

---

## 4. Resource Allocation & RAM Optimization

- **Base Alpine footprint**: ~8 MB.
- **Python Runtime + Dependencies**: ~45 MB.
- **OpenVPN + WireGuard daemons**: ~12 MB.
- **Total Memory Footprint**: `< 75 MB` RSS in steady state.
- Supports routers with as little as 128 MB RAM (e.g. MikroTik hEX or CHR 128MB).

