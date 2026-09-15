"""Netrava Open Government Video Intelligence Fabric — Central Gateway.

Reference Implementation: Gujarat Police Innovation Challenge 2026.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from core.config import settings
from db.session import init_db
from services.alert_service import ws_manager
from routers import (
    cameras,
    streams,
    events,
    vehicles,
    watchlists,
    alerts,
    investigations,
    evidence,
    gis,
    system,
    audit
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure evidence directory and initialize DB tables
    os.makedirs(settings.EVIDENCE_LOCAL_STORAGE_DIR, exist_ok=True)
    await init_db()
    print("\n" + "="*60)
    print(f"  NETRAVA VIDEO INTELLIGENCE FABRIC [v{settings.VERSION}]")
    print(f"  State Deployment: {settings.DEFAULT_STATE} Police Innovation")
    print(f"  Operational Mode: {settings.APP_MODE.upper()}")
    print("="*60 + "\n")
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Open Government Video Intelligence Fabric & Cross-Camera Investigation Platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local evidence static directory
os.makedirs(settings.EVIDENCE_LOCAL_STORAGE_DIR, exist_ok=True)
app.mount("/static/evidence", StaticFiles(directory=settings.EVIDENCE_LOCAL_STORAGE_DIR), name="evidence")

# Include Routers
app.include_router(cameras.router, prefix=settings.API_V1_STR)
app.include_router(streams.router, prefix=settings.API_V1_STR)
app.include_router(events.router, prefix=settings.API_V1_STR)
app.include_router(vehicles.router, prefix=settings.API_V1_STR)
app.include_router(watchlists.router, prefix=settings.API_V1_STR)
app.include_router(alerts.router, prefix=settings.API_V1_STR)
app.include_router(investigations.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(gis.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)


@app.websocket("/api/v1/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """Sub-second WebSocket push endpoint for real-time watchlist and critical surveillance alerts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keepalive listener
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


@app.get("/")
async def root():
    return {
        "platform": "NETRAVA",
        "tagline": "Open Government Video Intelligence Fabric",
        "version": settings.VERSION,
        "mode": settings.APP_MODE,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
