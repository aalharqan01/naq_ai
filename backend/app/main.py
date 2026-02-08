"""Dhakira — Qatar Heritage AI Assistant — FastAPI application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db

logger = logging.getLogger("dhakira")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting Dhakira — Qatar Heritage AI Assistant")

    # Ensure directories exist
    for dir_path in [
        settings.audio_dir,
        settings.documents_dir,
        settings.processed_dir,
        settings.chroma_persist_dir,
    ]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize database
    init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Dhakira")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="AI-powered heritage preservation and exploration platform "
    "for the National Archives of Qatar.",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────

from app.routers import documents, ingest, query  # noqa: E402

app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])


# ── Health Check ──────────────────────────────────────────────────


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.app_version,
        "app": settings.app_title,
    }
