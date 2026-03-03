"""Health check router."""
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Returns service status."""
    return {"status": "ok", "service": "Learning Tracker API"}
