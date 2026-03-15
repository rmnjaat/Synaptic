"""Health check router."""
from fastapi import APIRouter

from app.services.gdrive_sync import mark_modified, trigger_manual_sync

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Returns service status."""
    return {"status": "ok", "service": "Learning Tracker API"}


@router.post("/api/sync")
def manual_sync():
    """Immediately sync all tables to Google Drive."""
    success = trigger_manual_sync()
    if success:
        return {"status": "ok", "message": "Sync completed successfully."}
    return {"status": "error", "message": "Sync service not initialized. Check credentials."}
