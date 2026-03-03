"""Search router."""
from fastapi import APIRouter, Depends, Query
from app.schemas.search import SearchResponse
from app.schemas.common import APIResponse
from app.services.search import SearchService
from app.dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/global", response_model=APIResponse[SearchResponse])
def global_search(
    user_id: int = Query(..., description="User ID to scope the search"),
    q: str = Query(..., min_length=2, description="Search query (min 2 chars)"),
    svc: SearchService = Depends(get_search_service),
):
    """Global case-insensitive search across topics, subtopics, notes, and projects."""
    result = svc.search(user_id, q)
    return APIResponse.ok(data=result)
