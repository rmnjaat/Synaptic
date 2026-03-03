"""Project Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.project import ProjectStatusEnum


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    status: ProjectStatusEnum = ProjectStatusEnum.planning
    is_public: bool = True
    user_id: int


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    is_public: Optional[bool] = None


class AddTopicsToProject(BaseModel):
    topic_ids: List[int]


class ProjectRead(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    status: ProjectStatusEnum
    is_public: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
