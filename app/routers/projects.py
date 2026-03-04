"""Projects router."""
from fastapi import APIRouter, Depends, status
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, AddTopicsToProject
from app.schemas.common import APIResponse
from app.services.project import ProjectService
from app.dependencies import get_project_service
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/create", response_model=APIResponse[ProjectRead], status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, svc: ProjectService = Depends(get_project_service)):
    project = svc.create_project(payload.model_dump())
    return APIResponse.ok(data=ProjectRead.model_validate(project), message="Project created.")


@router.get("/{project_id}", response_model=APIResponse[ProjectRead])
def get_project(project_id: int, svc: ProjectService = Depends(get_project_service)):
    project = svc.get_project(project_id)
    return APIResponse.ok(data=ProjectRead.model_validate(project))


@router.patch("/{project_id}", response_model=APIResponse[ProjectRead])
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    svc: ProjectService = Depends(get_project_service),
):
    """Update a project's details."""
    project = svc.update_project(project_id, payload.model_dump(exclude_unset=True))
    return APIResponse.ok(data=ProjectRead.model_validate(project), message="Project updated.")


@router.post("/{project_id}/mark-completed", response_model=APIResponse[ProjectRead])
def mark_project_completed(project_id: int, svc: ProjectService = Depends(get_project_service)):
    project = svc.mark_completed(project_id)
    return APIResponse.ok(data=ProjectRead.model_validate(project), message="Project marked as completed.")


@router.post("/{project_id}/add-topics", response_model=APIResponse[ProjectRead])
def add_topics_to_project(
    project_id: int,
    payload: AddTopicsToProject,
    svc: ProjectService = Depends(get_project_service),
):
    project = svc.add_topics(project_id, payload.topic_ids)
    return APIResponse.ok(data=ProjectRead.model_validate(project), message="Topics added to project.")


@router.delete("/{project_id}", response_model=APIResponse[None])
def delete_project(project_id: int, svc: ProjectService = Depends(get_project_service)):
    svc.delete_project(project_id)
    return APIResponse.ok(message="Project deleted.")
