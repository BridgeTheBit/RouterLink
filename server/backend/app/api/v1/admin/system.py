from typing import List
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.models.audit import AuditLog
from app.schemas.system import SystemStats, AuditLogResponse, BackupInfo
from app.services.system_service import SystemService

router = APIRouter(prefix="/system", tags=["Admin - System"])


@router.get("/stats", response_model=SystemStats)
def get_system_stats(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    return SystemService.get_system_stats(db)


@router.get("/backups", response_model=List[BackupInfo])
def list_backups(admin: AdminUser = Depends(get_current_admin)):
    return SystemService.list_backups()


@router.post("/backups")
def create_backup(admin: AdminUser = Depends(get_current_admin)):
    file_path = SystemService.create_backup()
    return {"message": "Backup created successfully", "filename": file_path.name}


@router.get("/backups/{filename}/download")
def download_backup(filename: str, admin: AdminUser = Depends(get_current_admin)):
    from app.config import settings
    file_path = settings.DATA_DIR / "backups" / filename
    if not file_path.exists():
        from app.core.exceptions import NotFoundHTTP
        raise NotFoundHTTP("Backup file not found")
    return FileResponse(file_path.as_posix(), media_type="application/octet-stream", filename=filename)


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    logs = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    results = []
    for l in logs:
        results.append(AuditLogResponse(
            id=l.id,
            actor_type=l.actor_type,
            actor_id=l.actor_id,
            action=l.action,
            target_entity=l.target_entity,
            ip_address=l.ip_address,
            created_at=l.created_at.isoformat()
        ))
    return results

