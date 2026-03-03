"""SubTopic Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.topic import StatusEnum


class SubTopicCreate(BaseModel):
    name: str
    order_index: int = 0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()


class SubTopicUpdate(BaseModel):
    name: Optional[str] = None
    order_index: Optional[int] = None


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
