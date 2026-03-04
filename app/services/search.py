"""SearchService — validates queries and formats grouped search results."""
from fastapi import HTTPException
from app.repositories.search import SearchRepository
from app.schemas.search import (
    SearchResponse,
    TopicSearchResult,
    SubTopicSearchResult,
    NoteSearchResult,
    ProjectSearchResult,
)


class SearchService:
    def __init__(self, repo: SearchRepository):
        self.repo = repo

    def search(self, user_id: int, query: str) -> SearchResponse:
        self.validate_search_query(query)
        raw = self.repo.search_all(user_id, query)
        return self.format_search_results(query, raw)

    def validate_search_query(self, query: str) -> None:
        if not query or len(query.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "data": None,
                    "message": "Search query must be at least 2 characters.",
                    "error": {"code": "INVALID_QUERY", "details": None},
                },
            )

    def format_search_results(self, query: str, raw: dict) -> SearchResponse:
        topics = [
            TopicSearchResult(id=t.id, name=t.name, category=t.category)
            for t in raw.get("topics", [])
        ]
        sub_topics = [
            SubTopicSearchResult(id=s.id, name=s.name, parent_topic_id=s.topic_id)
            for s in raw.get("sub_topics", [])
        ]
        notes = [
            NoteSearchResult(id=n.id, title=n.title, topic_id=n.topic_id)
            for n in raw.get("notes", [])
        ]
        projects = [
            ProjectSearchResult(
                id=p.id,
                name=p.name,
                description=p.description,
                tech_stack=p.tech_stack,
            )
            for p in raw.get("projects", [])
        ]
        total = len(topics) + len(sub_topics) + len(notes) + len(projects)
        return SearchResponse(
            query=query,
            total_count=total,
            topics=topics,
            sub_topics=sub_topics,
            notes=notes,
            projects=projects,
        )
