from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_admin
from app.models.admin import AdminUser
from app.models.protocol import ProtocolConfig
from app.models.session import Session as VPNSession
from app.schemas.protocol import (
    ProtocolConfigResponse,
    ProtocolUpdate,
    ProtocolActionRequest,
    ProtocolLogResponse
)
from app.protocols.manager import protocol_manager
from app.core.exceptions import NotFoundHTTP, BadRequestHTTP

router = APIRouter(prefix="/protocols", tags=["Admin - Protocols"])


@router.get("", response_model=List[ProtocolConfigResponse])
def list_protocols(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    configs = db.query(ProtocolConfig).all()
    results = []
    for cfg in configs:
        engine = protocol_manager.get_engine(cfg.protocol_name)
        status_val = engine.get_status() if engine else ("running" if cfg.is_enabled else "stopped")
        
        # Count connected clients for this protocol
        connected_count = db.query(VPNSession).filter(
            VPNSession.protocol == cfg.protocol_name,
            VPNSession.is_active == True
        ).count()

        results.append(ProtocolConfigResponse(
            id=cfg.id,
            protocol_name=cfg.protocol_name,
            is_enabled=cfg.is_enabled,
            listen_port=cfg.listen_port,
            transport_type=cfg.transport_type,
            cipher_settings=cfg.cipher_settings,
            status=status_val,
            connected_clients=connected_count
        ))
    return results


@router.put("/{name}", response_model=ProtocolConfigResponse)
def update_protocol(
    name: str,
    payload: ProtocolUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    cfg = db.query(ProtocolConfig).filter(ProtocolConfig.protocol_name == name).first()
    if not cfg:
        raise NotFoundHTTP(f"Protocol '{name}' not found")

    if payload.is_enabled is not None:
        cfg.is_enabled = payload.is_enabled
    if payload.listen_port is not None:
        cfg.listen_port = payload.listen_port
    if payload.cipher_settings is not None:
        cfg.cipher_settings = payload.cipher_settings

    db.commit()
    db.refresh(cfg)

    engine = protocol_manager.get_engine(cfg.protocol_name)
    status_val = engine.get_status() if engine else "running"

    return ProtocolConfigResponse(
        id=cfg.id,
        protocol_name=cfg.protocol_name,
        is_enabled=cfg.is_enabled,
        listen_port=cfg.listen_port,
        transport_type=cfg.transport_type,
        cipher_settings=cfg.cipher_settings,
        status=status_val,
        connected_clients=0
    )


@router.post("/{name}/action")
def perform_protocol_action(
    name: str,
    payload: ProtocolActionRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    engine = protocol_manager.get_engine(name)
    if not engine:
        raise NotFoundHTTP(f"Protocol '{name}' not found")

    action = payload.action.lower()
    success = False
    if action == "start":
        success = engine.start()
    elif action == "stop":
        success = engine.stop()
    elif action == "restart":
        success = engine.restart()

    return {"protocol": name, "action": action, "success": success, "status": engine.get_status()}


@router.get("/{name}/logs", response_model=ProtocolLogResponse)
def get_protocol_logs(
    name: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    engine = protocol_manager.get_engine(name)
    if not engine:
        raise NotFoundHTTP(f"Protocol '{name}' not found")

    logs = engine.get_recent_logs(lines=100)
    return ProtocolLogResponse(protocol_name=name, lines=logs)

