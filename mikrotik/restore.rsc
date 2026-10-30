# ==============================================================================
# RouterLink Restore Script for MikroTik RouterOS 7
# ==============================================================================

:put "To restore RouterLink database & settings:"
:put "1. Upload your database file to /routerlink/data/db/routerlink.db"
:put "2. Restart the RouterLink container using:"
:put "   /container/stop [find comment=\"RouterLink Gateway Service\"]"
:put "   /container/start [find comment=\"RouterLink Gateway Service\"]"

