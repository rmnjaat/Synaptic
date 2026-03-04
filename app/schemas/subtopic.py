"""SubTopic Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.models.topic import StatusEnum


class LinkItem(BaseModel):
    label: str
    url: str


class SubTopicCreate(BaseModel):
    name: str
    description: Optional[str] = None
    links: Optional[List[LinkItem]] = None
    order_index: int = 0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class SubTopicUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    links: Optional[List[LinkItem]] = None
    order_index: Optional[int] = None


class SubTopicRead(BaseModel):
    id: int
    topic_id: int
    name: str
    description: Optional[str] = None
    links: Optional[str] = None  # stored as JSON string in DB
    status: StatusEnum
    completed_at: Optional[datetime] = None
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
