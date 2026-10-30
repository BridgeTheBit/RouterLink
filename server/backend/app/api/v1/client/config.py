from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.core.dependencies import get_current_client
from app.models.user import User
from app.models.protocol import ProtocolConfig
from app.protocols.manager import protocol_manager
from app.core.exceptions import ProtocolNotAllowedException, NotFoundHTTP

router = APIRouter(prefix="/client/config", tags=["Client - VPN Configs"])


@router.get("/openvpn")
def get_openvpn_profile(
    proto: str = Query("tcp", pattern="^(tcp|udp)$"),
    user: User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    protocol_name = f"openvpn_{proto}"
    if protocol_name not in user.allowed_protocols:
        raise ProtocolNotAllowedException(f"Protocol '{protocol_name}' is not allowed for your account")

    engine = protocol_manager.get_engine(protocol_name)
    if not engine:
        raise NotFoundHTTP("OpenVPN engine not available")

    # Fetch configured port from DB
    cfg = db.query(ProtocolConfig).filter(ProtocolConfig.protocol_name == protocol_name).first()
    port = cfg.listen_port if cfg else engine.default_port

    config_content = engine.generate_client_config(user, server_host=settings.SERVER_PUBLIC_HOST, port=port)
    return Response(
        content=config_content,
        media_type="application/x-openvpn-profile",
        headers={"Content-Disposition": f'attachment; filename="routerlink_{user.username}_{proto}.ovpn"'}
    )


@router.get("/wireguard")
def get_wireguard_profile(
    user: User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    if "wireguard" not in user.allowed_protocols:
        raise ProtocolNotAllowedException("WireGuard protocol is not allowed for your account")

    engine = protocol_manager.get_engine("wireguard")
    if not engine:
        raise NotFoundHTTP("WireGuard engine not available")

    cfg = db.query(ProtocolConfig).filter(ProtocolConfig.protocol_name == "wireguard").first()
    port = cfg.listen_port if cfg else engine.default_port

    config_content = engine.generate_client_config(user, server_host=settings.SERVER_PUBLIC_HOST, port=port)
    return Response(
        content=config_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="routerlink_{user.username}.conf"'}
    )

