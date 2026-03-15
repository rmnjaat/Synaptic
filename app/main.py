"""
Learning Tracker API — FastAPI application entry point.
"""
import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Import all models so SQLAlchemy can register them
import app.models.user  # noqa: F401
import app.models.topic  # noqa: F401
import app.models.subtopic  # noqa: F401
import app.models.note  # noqa: F401
import app.models.resource  # noqa: F401
import app.models.project  # noqa: F401
import app.models.streak  # noqa: F401

from app.database import engine, Base
from app.routers import health, topics, subtopics, notes, projects, search, users
from app.routers import auth as auth_router
from app.services.gdrive_sync import start_gdrive_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("learning_tracker")

# Add FileHandler to main logger
log_file = os.path.join(os.getcwd(), "app.log")
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
logger.addHandler(file_handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all tables on startup and begin background sync."""
    logger.info("Starting Learning Tracker API — creating database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema created.")
    
    # Start Google Drive Background Sync (if credentials exist)
    try:
        start_gdrive_sync()
    except Exception as e:
        logger.error("GDrive sync failed to start: %s — app will continue without sync.", e)
    
    yield
    logger.info("Shutting down Learning Tracker API.")


app = FastAPI(
    title="Learning Tracker API",
    description=(
        "A REST API for tracking learning progress across categories. "
        "Built with FastAPI + SQLite in-memory using Service-Repository architecture."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth_router.router, prefix="/api")
app.include_router(topics.router, prefix="/api")
app.include_router(subtopics.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(users.router, prefix="/api")


# ── Root redirect → Swagger UI ───────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    """Redirect browser to the interactive API documentation."""
    return RedirectResponse(url="/docs")



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": "An internal server error occurred.",
            "error": {"code": "INTERNAL_ERROR", "details": str(exc)},
        },
    )
