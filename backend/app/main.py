"""
ThreatShield AI — FastAPI Application Entry Point

Initializes the database, starts the background log watcher,
registers all API routers, exposes Prometheus metrics, and
manages the WebSocket /ws/feed endpoint.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.database import engine, Base
from app.config import get_settings
from app.routers import attacks, stats, countries, top_ips, timeline, categories
from app.websocket.feed import manager
from app.ingestion.log_watcher import watch_logs

settings = get_settings()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: runs startup + shutdown logic.
    - Creates DB tables on startup
    - Starts background log watcher task
    - Cancels watcher cleanly on shutdown
    """
    # Startup
    logger.info("[ThreatShield] Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("[ThreatShield] Database ready.")

    logger.info("[ThreatShield] Starting log watcher background task...")
    watcher_task = asyncio.create_task(watch_logs())

    yield  # Application is running

    # Shutdown
    logger.info("[ThreatShield] Shutting down log watcher...")
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass
    logger.info("[ThreatShield] Shutdown complete.")


# ─── FastAPI app ──────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "ThreatShield AI — Backend API",
    description = (
        "Real-time cybersecurity threat intelligence backend. "
        "Ingests Cowrie SSH/Telnet and fake web-login honeypot events, "
        "classifies threats, and streams updates via WebSocket."
    ),
    version     = "1.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
origins = [o.strip() for o in settings.BACKEND_CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins     = origins,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Prometheus metrics ───────────────────────────────────────────────────────
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ─── API Routers ──────────────────────────────────────────────────────────────
app.include_router(attacks.router)
app.include_router(stats.router)
app.include_router(countries.router)
app.include_router(top_ips.router)
app.include_router(timeline.router)
app.include_router(categories.router)


# ─── Health endpoints ─────────────────────────────────────────────────────────

@app.get("/", tags=["health"])
async def root():
    return {
        "service": "ThreatShield AI Backend",
        "status":  "operational",
        "version": "1.0.0",
        "docs":    "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


# ─── WebSocket feed ───────────────────────────────────────────────────────────

@app.websocket("/ws/feed")
async def websocket_feed(websocket: WebSocket):
    """
    Real-time attack event feed.
    The log watcher pushes events via broadcast_event(); this endpoint
    keeps the connection alive and handles disconnects gracefully.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive keeps the connection alive (ping/pong)
            # We don't process client messages, but must read to detect disconnects
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"[WS] Unexpected error: {e}")
        await manager.disconnect(websocket)
