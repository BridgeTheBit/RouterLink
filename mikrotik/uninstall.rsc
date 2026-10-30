# ==============================================================================
# RouterLink Clean Teardown & Uninstall Script for MikroTik RouterOS 7
# Safely removes container, VETH, bridge, and labeled NAT rules
# Does NOT touch any existing customer configs or firewall rules
# ==============================================================================

:log info "=== [RouterLink] Starting Safe Teardown ==="
:put "=========================================================="
:put "           RouterLink Clean Teardown Process              "
:put "=========================================================="

# 1. Stop and remove container
:local cId [/container/find comment="RouterLink Gateway Service"]
:if ([:len $cId] > 0) do={
    :put "[1/5] Stopping and removing RouterLink container..."
    :do { /container/stop $cId } on-error={}
    :delay 3s
    :do { /container/remove $cId } on-error={}
}

# 2. Remove Labeled NAT Rules
:put "[2/5] Removing labeled RouterLink NAT rules..."
/ip/firewall/nat/remove [find comment~"^RouterLink "]

# 3. Remove Container Mounts and Environment variables
:put "[3/5] Cleaning container mounts and environment variables..."
/container/mounts/remove [find name="routerlink-data"]
/container/envs/remove [find name="routerlink-env"]

# 4. Remove VETH and Bridge
:put "[4/5] Removing dedicated VETH and bridge-routerlink..."
/interface/bridge/port/remove [find interface="veth-routerlink"]
/interface/veth/remove [find name="veth-routerlink"]
/ip/address/remove [find interface="bridge-routerlink"]
/interface/bridge/remove [find name="bridge-routerlink"]

# 5. Summary and Persistent Data Notice
:put "[5/5] Teardown complete."
:put "=========================================================="
:put " RouterLink network services and container removed!       "
:put " Note: Your user data was preserved in /routerlink/data    "
:put " To permanently delete all user databases, run:           "
:put "   /file/remove [find name~\"^routerlink\"]               "
:put "=========================================================="
:log info "=== [RouterLink] Teardown completed successfully ==="

