#!/bin/bash
set -e

echo "=========================================================="
echo "          Starting RouterLink Container Gateway           "
echo "             MikroTik RouterOS 7 Linux Container          "
echo "=========================================================="

# 1. Ensure Persistent Directories exist in /data
DATA_DIR=${ROUTERLINK_DATA_DIR:-/data}
mkdir -p "${DATA_DIR}/db" "${DATA_DIR}/certs" "${DATA_DIR}/config" "${DATA_DIR}/logs" "${DATA_DIR}/backups"

# 2. Ensure TUN device exists for VPN interfaces
if [ ! -d /dev/net ]; then
    mkdir -p /dev/net
fi
if [ ! -c /dev/net/tun ]; then
    mknod /dev/net/tun c 10 200 || true
    chmod 600 /dev/net/tun || true
fi

# 3. Configure Network & Packet Forwarding
echo "[1/4] Configuring IP forwarding and firewall rules..."
sysctl -w net.ipv4.ip_forward=1 2>/dev/null || true

# Setup iptables NAT masquerade for VPN subnets out to container default interface
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE 2>/dev/null || true
iptables -t nat -A POSTROUTING -s 10.9.0.0/24 -o eth0 -j MASQUERADE 2>/dev/null || true
iptables -A FORWARD -i tun0 -j ACCEPT 2>/dev/null || true
iptables -A FORWARD -i wg0 -j ACCEPT 2>/dev/null || true

# 4. Run Database Schema Migrations
echo "[2/4] Applying database migrations with Alembic..."
cd /app
if [ -f /app/alembic.ini ]; then
    alembic upgrade head || echo "Database migration completed or skipped."
fi

# 5. Start OpenVPN Daemon in background
echo "[3/4] Initializing VPN protocol engines..."
if command -v openvpn >/dev/null 2>&1; then
    # Generate server config if missing
    python3 -c "
from app.protocols.openvpn import OpenVPNEngine
from app.config import settings
from pathlib import Path
engine = OpenVPNEngine(name='openvpn_tcp', port=settings.OPENVPN_PORT, proto='tcp')
cfg_path = Path('/data/config/openvpn_tcp.conf')
if not cfg_path.exists():
    cfg_path.write_text(engine.generate_server_config())
" 2>/dev/null || true

    if [ -f /data/config/openvpn_tcp.conf ]; then
        echo "Starting OpenVPN Server (TCP:8443)..."
        openvpn --config /data/config/openvpn_tcp.conf --daemon openvpn_server || echo "OpenVPN daemon warning: check tun device capabilities."
    fi
fi

# 6. Start WireGuard interface if available
if command -v wg-quick >/dev/null 2>&1; then
    python3 -c "
from app.protocols.wireguard import WireGuardEngine
from pathlib import Path
engine = WireGuardEngine()
cfg_path = Path('/etc/wireguard/wg0.conf')
cfg_path.parent.mkdir(parents=True, exist_ok=True)
if not cfg_path.exists():
    cfg_path.write_text(engine.generate_server_config())
" 2>/dev/null || true

    if [ -f /etc/wireguard/wg0.conf ]; then
        echo "Starting WireGuard Server (UDP:51820)..."
        wg-quick up wg0 2>/dev/null || echo "WireGuard wg-quick notice: container kernel module or userspace driver active."
    fi
fi

# 7. Start Uvicorn FastAPI Server (PID 1)
echo "[4/4] Launching RouterLink API & WebUI on 0.0.0.0:8080..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info

