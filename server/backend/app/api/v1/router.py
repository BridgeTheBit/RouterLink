from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.admin.users import router as admin_users_router
from app.api.v1.admin.protocols import router as admin_protocols_router
from app.api.v1.admin.sessions import router as admin_sessions_router
from app.api.v1.admin.system import router as admin_system_router
from app.api.v1.client.auth import router as client_auth_router
from app.api.v1.client.config import router as client_config_router
from app.api.v1.client.heartbeat import router as client_heartbeat_router

api_v1_router = APIRouter(prefix="/api/v1")

# Authentication
api_v1_router.include_router(auth_router)

# Admin Endpoints
admin_router = APIRouter(prefix="/admin")
admin_router.include_router(admin_users_router)
admin_router.include_router(admin_protocols_router)
admin_router.include_router(admin_sessions_router)
admin_router.include_router(admin_system_router)
api_v1_router.include_router(admin_router)

# Client Endpoints
api_v1_router.include_router(client_auth_router)
api_v1_router.include_router(client_config_router)
api_v1_router.include_router(client_heartbeat_router)

