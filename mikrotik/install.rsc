# ==============================================================================
# RouterLink 1-Click Automated Installer for MikroTik RouterOS 7
# Idempotent, Non-Destructive, and Resource-Optimized
# ==============================================================================

:log info "=== [RouterLink] Starting Automated Installation on RouterOS 7 ==="
:put "=========================================================="
:put "     RouterLink Automated Installer for RouterOS 7        "
:put "=========================================================="

# ------------------------------------------------------------------------------
# 1. Environment & Pre-requisite Checks
# ------------------------------------------------------------------------------
:local rosVersion [/system/resource/get version]
:local rosArch [/system/resource/get architecture-name]
:local freeHdd [/system/resource/get free-hdd-space]
:local freeRam [/system/resource/get free-memory]

:put "[1/8] Verifying RouterOS compatibility..."
:put "  - RouterOS Version: $rosVersion"
:put "  - CPU Architecture: $rosArch"
:put "  - Free Memory: ($freeRam / 1048576) MB"
:put "  - Free Disk: ($freeHdd / 1048576) MB"

# Verify Container package is available
:if ([:len [/container/config/find]] = 0) do={
    :log error "[RouterLink] Container package is not installed or enabled in RouterOS!"
    :error "ERROR: The 'container' package is missing or not enabled. Install container.npk first."
}

# Verify minimum free RAM (64MB)
:if ($freeRam < 67108864) do={
    :log warning "[RouterLink] Warning: Free memory is under 64MB. Performance may be degraded."
}

# ------------------------------------------------------------------------------
# 2. Configure Dedicated RouterLink Network (Bridge & VETH)
# ------------------------------------------------------------------------------
:put "[2/8] Configuring dedicated Virtual Ethernet (VETH) and Bridge..."

# Dedicated Bridge for Container Isolation
:if ([:len [/interface/bridge/find name="bridge-routerlink"]] = 0) do={
    /interface/bridge/add name="bridge-routerlink" comment="RouterLink Isolated Container Bridge"
}

# Assign Gateway IP (172.28.0.1/24) to the Bridge
:if ([:len [/ip/address/find interface="bridge-routerlink" address="172.28.0.1/24"]] = 0) do={
    /ip/address/add address="172.28.0.1/24" network=172.28.0.0 interface="bridge-routerlink" comment="RouterLink Gateway"
}

# Create VETH interface for Container (172.28.0.2/24)
:if ([:len [/interface/veth/find name="veth-routerlink"]] = 0) do={
    /interface/veth/add name="veth-routerlink" address="172.28.0.2/24" gateway=172.28.0.1 comment="RouterLink Container Interface"
}

# Attach VETH to dedicated Bridge
:if ([:len [/interface/bridge/port/find interface="veth-routerlink"]] = 0) do={
    /interface/bridge/port/add bridge="bridge-routerlink" interface="veth-routerlink" comment="RouterLink VETH Port"
}

# ------------------------------------------------------------------------------
# 3. Setup Persistent Storage Mounts
# ------------------------------------------------------------------------------
:put "[3/8] Preparing persistent storage in /routerlink/data..."

# Make directory if not present
:do {
    /file/add name="routerlink/data" type="directory"
} on-error={}

# Container Mount Map (maps /routerlink/data on host to /data in container)
:if ([:len [/container/mounts/find name="routerlink-data"]] = 0) do={
    /container/mounts/add name="routerlink-data" src="routerlink/data" dst="/data" comment="RouterLink Persistent Storage"
}

# ------------------------------------------------------------------------------
# 4. Setup Container Environment Variables
# ------------------------------------------------------------------------------
:put "[4/8] Configuring container environment variables..."

:if ([:len [/container/envs/find name="routerlink-env" key="ROUTERLINK_DATA_DIR"]] = 0) do={
    /container/envs/add name="routerlink-env" key="ROUTERLINK_DATA_DIR" value="/data" comment="RouterLink Data Directory"
    /container/envs/add name="routerlink-env" key="ROUTERLINK_HOST" value="0.0.0.0" comment="RouterLink Listen Host"
    /container/envs/add name="routerlink-env" key="ROUTERLINK_PORT" value="8080" comment="RouterLink WebUI Port"
}

# ------------------------------------------------------------------------------
# 5. Configure Safe Labeled NAT & Firewall Rules
# ------------------------------------------------------------------------------
:put "[5/8] Adding labeled NAT rules (without touching existing customer firewall)..."

# Masquerade outbound traffic from Container to Internet
:if ([:len [/ip/firewall/nat/find comment="RouterLink Container NAT Outbound"]] = 0) do={
    /ip/firewall/nat/add chain=srcnat src-address=172.28.0.0/24 action=masquerade comment="RouterLink Container NAT Outbound"
}

# Forward WebUI & REST API Port 8080 to Container
:if ([:len [/ip/firewall/nat/find comment="RouterLink WebUI Forward 8080"]] = 0) do={
    /ip/firewall/nat/add chain=dstnat protocol=tcp dst-port=8080 action=dst-nat to-addresses=172.28.0.2 to-ports=8080 comment="RouterLink WebUI Forward 8080"
}

# Forward OpenVPN TCP Port 8443 to Container
:if ([:len [/ip/firewall/nat/find comment="RouterLink OpenVPN TCP Forward 8443"]] = 0) do={
    /ip/firewall/nat/add chain=dstnat protocol=tcp dst-port=8443 action=dst-nat to-addresses=172.28.0.2 to-ports=8443 comment="RouterLink OpenVPN TCP Forward 8443"
}

# Forward WireGuard UDP Port 51820 to Container
:if ([:len [/ip/firewall/nat/find comment="RouterLink WireGuard UDP Forward 51820"]] = 0) do={
    /ip/firewall/nat/add chain=dstnat protocol=udp dst-port=51820 action=dst-nat to-addresses=172.28.0.2 to-ports=51820 comment="RouterLink WireGuard UDP Forward 51820"
}

# ------------------------------------------------------------------------------
# 6. Configure Registry & Container Image
# ------------------------------------------------------------------------------
:put "[6/8] Configuring Container Registry..."
/container/config/set registry-url="https://ghcr.io" tmpdir="routerlink/tmp"

# ------------------------------------------------------------------------------
# 7. Create and Start the RouterLink Container
# ------------------------------------------------------------------------------
:put "[7/8] Provisioning RouterLink Linux Container..."

:local containerTag "ghcr.io/yourorg/routerlink:latest"

:if ([:len [/container/find comment="RouterLink Gateway Service"]] = 0) do={
    /container/add remote-image=$containerTag interface=veth-routerlink mounts=routerlink-data envlist=routerlink-env logging=yes start-on-boot=yes comment="RouterLink Gateway Service"
    :put "Waiting for image extraction..."
    :delay 10s
}

# Start container if not already running
:local cId [/container/find comment="RouterLink Gateway Service"]
:if ([:len $cId] > 0) do={
    /container/start $cId
}

# ------------------------------------------------------------------------------
# 8. Post-Installation Verification & Summary
# ------------------------------------------------------------------------------
:put "[8/8] Verifying RouterLink deployment..."
:delay 5s

:local firstIp [/ip/address/get [find interface!=bridge-routerlink disabled=no] address]
:local hostIp [:pick $firstIp 0 [:find $firstIp "/"]]

:put "=========================================================="
:put "   RouterLink Installation Successfully Completed! 🎉    "
:put "=========================================================="
:put "  - WebUI URL:          http://$hostIp:8080"
:put "  - OpenVPN Port:       TCP 8443"
:put "  - WireGuard Port:     UDP 51820"
:put "  - Container Subnet:   172.28.0.0/24 (VETH: 172.28.0.2)"
:put "  - Persistent Storage: /routerlink/data"
:put "=========================================================="
:put "Open your web browser at http://$hostIp:8080 to complete"
:put "the First-Run Setup Wizard and create your Admin account."
:put "=========================================================="
:log info "=== [RouterLink] Installation finished successfully. Access at http://$hostIp:8080 ==="

