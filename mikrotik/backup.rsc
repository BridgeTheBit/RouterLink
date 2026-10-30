# ==============================================================================
# RouterLink Database & Config Backup Script for MikroTik RouterOS 7
# ==============================================================================

:local timeStamp [/system/clock/get date]
:local backupName "routerlink-backup-$timeStamp"

:log info "[RouterLink] Creating system backup: $backupName"
:put "Creating system backup..."

# Backup router configuration
/system/backup/save name=$backupName

:put "Backup completed: $backupName.backup"
:put "To export user data directory, download the /routerlink/data folder via FTP or SFTP."

