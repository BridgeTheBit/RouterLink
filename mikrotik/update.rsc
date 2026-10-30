# ==============================================================================
# RouterLink In-Place Safe Update Script for MikroTik RouterOS 7
# Preserves all user databases, certificates, and settings in /routerlink/data
# ==============================================================================

:log info "=== [RouterLink] Starting In-Place Update ==="
:put "=========================================================="
:put "          RouterLink Container Update Process             "
:put "=========================================================="

:local cId [/container/find comment="RouterLink Gateway Service"]

:if ([:len $cId] = 0) do={
    :put "ERROR: RouterLink container not found. Run install.rsc first."
    :error "RouterLink container not found."
}

:put "[1/4] Stopping active RouterLink container..."
/container/stop $cId
:delay 5s

:put "[2/4] Removing previous container instance (Data in /routerlink/data is preserved)..."
/container/remove $cId
:delay 2s

:put "[3/4] Pulling latest image tag and recreating container..."
/container/add remote-image="ghcr.io/yourorg/routerlink:latest" interface=veth-routerlink mounts=routerlink-data envlist=routerlink-env logging=yes start-on-boot=yes comment="RouterLink Gateway Service"
:delay 10s

:put "[4/4] Starting updated RouterLink container..."
:local newCId [/container/find comment="RouterLink Gateway Service"]
:if ([:len $newCId] > 0) do={
    /container/start $newCId
    :delay 5s
    :put "RouterLink successfully updated and started!"
    :log info "=== [RouterLink] Update completed successfully ==="
} else={
    :put "ERROR: Failed to start new container. Check system log."
    :log error "[RouterLink] Update container restart failed."
}

