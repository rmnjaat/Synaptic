"""Topic Pydantic schemas — category is now a free-form string."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.topic import StatusEnum


class TopicCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str               # ← any string — no enum restriction
    is_public: bool = True
    user_id: int

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("category must not be empty")
        # Normalise: lowercase, spaces → underscores
        return v.strip().lower().replace(" ", "_")

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 1000:
            raise ValueError("description must not exceed 1000 characters")
        return v


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[StatusEnum] = None
    is_public: Optional[bool] = None


class SubTopicRead(BaseModel):
    id: int
    topic_id: int
    name: str
    status: StatusEnum
    completed_at: Optional[datetime] = None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResourceRead(BaseModel):
    id: int
    topic_id: int
    title: str
    url: Optional[str] = None
    resource_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteReadBrief(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TopicRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    category: str               # ← plain string
    status: StatusEnum
    parent_topic_id: Optional[int] = None
    progress_percentage: float
    order_index: int
    is_public: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TopicDetailRead(TopicRead):
    subtopics: List[SubTopicRead] = []
    notes: List[NoteReadBrief] = []
    resources: List[ResourceRead] = []
