import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import psutil
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User
from app.models.session import Session as VPNSession
from app.schemas.system import SystemStats, BackupInfo


class SystemService:
    START_TIME = time.time()

    @classmethod
    def get_system_stats(cls, db: Session) -> SystemStats:
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        # Disk usage for the DATA_DIR or root
        disk_path = settings.DATA_DIR.as_posix() if settings.DATA_DIR.exists() else "/"
        disk = psutil.disk_usage(disk_path)

        uptime = int(time.time() - cls.START_TIME)

        total_users = db.query(User).count()
        online_users = db.query(func.count(func.distinct(VPNSession.user_id))).filter(VPNSession.is_active == True).scalar() or 0
        active_sessions = db.query(VPNSession).filter(VPNSession.is_active == True).count()

        upload_sum = db.query(func.sum(VPNSession.upload_bytes)).scalar() or 0
        download_sum = db.query(func.sum(VPNSession.download_bytes)).scalar() or 0

        return SystemStats(
            cpu_percent=round(cpu_pct, 1),
            ram_total_mb=round(mem.total / (1024 * 1024), 1),
            ram_used_mb=round(mem.used / (1024 * 1024), 1),
            ram_percent=round(mem.percent, 1),
            disk_total_gb=round(disk.total / (1024 * 1024 * 1024), 2),
            disk_used_gb=round(disk.used / (1024 * 1024 * 1024), 2),
            disk_percent=round(disk.percent, 1),
            uptime_seconds=uptime,
            total_users=total_users,
            online_users=online_users,
            active_sessions=active_sessions,
            total_upload_bytes=upload_sum,
            total_download_bytes=download_sum,
            total_traffic_bytes=upload_sum + download_sum
        )

    @classmethod
    def create_backup(cls) -> Path:
        backup_dir = settings.DATA_DIR / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"routerlink_backup_{timestamp}.sqlite"

        # Safe SQLite backup
        if settings.DB_PATH.exists():
            shutil.copy2(settings.DB_PATH, backup_file)
        return backup_file

    @classmethod
    def list_backups(cls) -> List[BackupInfo]:
        backup_dir = settings.DATA_DIR / "backups"
        if not backup_dir.exists():
            return []
        
        backups = []
        for file in sorted(backup_dir.glob("*.sqlite"), reverse=True):
            stat = file.stat()
            backups.append(BackupInfo(
                filename=file.name,
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            ))
        return backups

