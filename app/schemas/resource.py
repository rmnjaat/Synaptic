"""Resource Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.resource import ResourceTypeEnum


class ResourceCreate(BaseModel):
    title: str
    url: Optional[str] = None
    resource_type: ResourceTypeEnum = ResourceTypeEnum.link
    topic_id: int


class ResourceRead(BaseModel):
    id: int
    topic_id: int
    title: str
    url: Optional[str] = None
    resource_type: ResourceTypeEnum
    created_at: datetime

    model_config = {"from_attributes": True}
