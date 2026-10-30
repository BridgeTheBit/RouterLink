import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.api.v1.router import api_v1_router
from app.protocols.manager import protocol_manager
from app.services.pki_service import PKIService
from app.workers.accounting import accounting_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("routerlink")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing RouterLink Server...")
    
    # 1. Create DB tables if not present
    Base.metadata.create_all(bind=engine)
    
    # 2. Seed default protocols in database
    db = SessionLocal()
    try:
        protocol_manager.initialize_defaults(db)
    finally:
        db.close()

    # 3. Ensure PKI Certificates and Keys exist
    try:
        PKIService.ensure_pki()
        logger.info("PKI infrastructure initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize PKI: {e}")

    # 4. Start background accounting daemon
    accounting_worker.start()
    logger.info(f"RouterLink Backend v{settings.APP_VERSION} ready.")

    yield

    # Shutdown sequence
    logger.info("Shutting down RouterLink Server...")
    accounting_worker.stop()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise VPN Service Gateway & Management API for MikroTik RouterOS 7",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Endpoints
app.include_router(api_v1_router)

# Serve WebUI static files if built
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists() and (static_dir / "index.html").exists():
    assets_dir = static_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path.as_posix())
        return FileResponse((static_dir / "index.html").as_posix())
else:
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "online",
            "docs": "/docs",
            "api_v1": "/api/v1"
        }

