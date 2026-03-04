"""Search Pydantic schemas."""
from typing import List, Optional
from pydantic import BaseModel


class TopicSearchResult(BaseModel):
    id: int
    type: str = "topic"
    name: str
    category: str


class SubTopicSearchResult(BaseModel):
    id: int
    type: str = "sub_topic"
    name: str
    parent_topic_id: int


class NoteSearchResult(BaseModel):
    id: int
    type: str = "note"
    title: str
    topic_id: int


class ProjectSearchResult(BaseModel):
    id: int
    type: str = "project"
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    total_count: int
    topics: List[TopicSearchResult] = []
    sub_topics: List[SubTopicSearchResult] = []
    notes: List[NoteSearchResult] = []
    projects: List[ProjectSearchResult] = []
