from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.request_id import RequestIDMiddleware
from app.core.errors import DomainError, domain_error_handler
from app.core.init_db import init_database
from app.core.database import SessionLocal

# Module Routers
from app.modules.identity.router import router as identity_router
from app.modules.farms.router import router as farms_router
from app.modules.agriculture.router import router as agriculture_router
from app.modules.devices.router import router as devices_router
from app.modules.telemetry.router import router as telemetry_router
from app.modules.irrigation.router import router as irrigation_router
from app.modules.operations.router import router as operations_router
from app.modules.monitoring.router import router as monitoring_router
from app.modules.intelligence.router import router as intelligence_router
from app.modules.sync.router import router as sync_router
from app.modules.integrations.router import router as integrations_router
from app.modules.reporting.router import router as reporting_router
from app.modules.admin.router import router as admin_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed data
    init_database()
    yield

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="TerraNexus Open Agricultural Intelligence & Operations Platform API",
    lifespan=lifespan
)

# CORS & Request ID Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_exception_handler(DomainError, domain_error_handler)

# Include All Routers under /api/v1
app.include_router(identity_router, prefix=settings.api_v1_prefix)
app.include_router(farms_router, prefix=settings.api_v1_prefix)
app.include_router(agriculture_router, prefix=settings.api_v1_prefix)
app.include_router(devices_router, prefix=settings.api_v1_prefix)
app.include_router(telemetry_router, prefix=settings.api_v1_prefix)
app.include_router(irrigation_router, prefix=settings.api_v1_prefix)
app.include_router(operations_router, prefix=settings.api_v1_prefix)
app.include_router(monitoring_router, prefix=settings.api_v1_prefix)
app.include_router(intelligence_router, prefix=settings.api_v1_prefix)
app.include_router(sync_router, prefix=settings.api_v1_prefix)
app.include_router(integrations_router, prefix=settings.api_v1_prefix)
app.include_router(reporting_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)

@app.get("/health/live", tags=["health"])
async def liveness():
    return {"status": "ok", "service": "terranexus-api", "version": "1.0.0"}

@app.get("/health/ready", tags=["health"])
async def readiness():
    db_ok = False
    try:
        db = SessionLocal()
        db.execute("SELECT 1" if "sqlite" in settings.database_url else "SELECT 1")
        db.close()
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ready" if db_ok else "degraded",
        "dependencies": {
            "database": "connected" if db_ok else "unreachable",
            "redis": "configured",
            "mqtt": "configured"
        }
    }
