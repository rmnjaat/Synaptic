"""Note Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    is_public: bool = True
    user_id: int
    topic_id: int

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be empty")
        return v.strip()


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_public: Optional[bool] = None


class NoteRead(BaseModel):
    id: int
    user_id: int
    topic_id: int
    title: str
    content: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
