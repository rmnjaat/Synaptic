"""Users router — aggregated user-scoped endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any, Dict, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.schemas.topic import TopicRead
from app.schemas.project import ProjectRead
from app.schemas.common import APIResponse
from app.services.topic import TopicService
from app.services.project import ProjectService
from app.dependencies import get_topic_service, get_project_service, get_db
from app.models.user import User


class UserCreate(BaseModel):
    username: str
    email: str
    display_name: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    display_name: Optional[str] = None
    model_config = {"from_attributes": True}


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create", response_model=APIResponse[UserRead], status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        return APIResponse.ok(data=UserRead.model_validate(existing), message="User already exists.")
    user = User(username=payload.username, email=payload.email, display_name=payload.display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return APIResponse.ok(data=UserRead.model_validate(user), message="User created.")


@router.get("/by-username/{username}", response_model=APIResponse[UserRead])
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Lookup a user by username."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found."})
    return APIResponse.ok(data=UserRead.model_validate(user))


@router.get("/{user_id}", response_model=APIResponse[UserRead])
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail={"success": False, "message": "User not found."})
    return APIResponse.ok(data=UserRead.model_validate(user))


@router.get("/{user_id}/topics", response_model=APIResponse[Dict[str, Any]])
def get_user_topics(user_id: int, svc: TopicService = Depends(get_topic_service)):
    """Get all topics for a user, grouped by category."""
    result = svc.get_user_topics(user_id)
    # Serialize each topic list per category
    serialized = {
        cat: [TopicRead.model_validate(t).model_dump() for t in topics]
        for cat, topics in result["topics_by_category"].items()
    }
    return APIResponse.ok(data={"user_id": user_id, "topics_by_category": serialized})


@router.get("/{user_id}/progress", response_model=APIResponse[Dict[str, Any]])
def get_user_progress(user_id: int, svc: TopicService = Depends(get_topic_service)):
    """Get overall learning progress across all 8 categories."""
    result = svc.get_overall_progress(user_id)
    return APIResponse.ok(data=result)


@router.get("/{user_id}/categories/{category}", response_model=APIResponse[Dict[str, Any]])
def get_category_progress(
    user_id: int, category: str, svc: TopicService = Depends(get_topic_service)
):
    """Get progress statistics for a specific category."""
    result = svc.get_user_category_progress(user_id, category)
    return APIResponse.ok(data=result)


@router.get("/{user_id}/projects", response_model=APIResponse[List[ProjectRead]])
def get_user_projects(user_id: int, svc: ProjectService = Depends(get_project_service)):
    """Get all projects for a user."""
    projects = svc.get_user_projects(user_id)
    return APIResponse.ok(data=[ProjectRead.model_validate(p) for p in projects])
