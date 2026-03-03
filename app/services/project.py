"""ProjectService — project management business logic."""
from typing import List
from fastapi import HTTPException
from app.repositories.project import ProjectRepository


class ProjectService:
    def __init__(self, repo: ProjectRepository):
        self.repo = repo

    def create_project(self, project_data: dict):
        return self.repo.create(project_data)

    def mark_completed(self, project_id: int):
        project = self.repo.mark_completed(project_id)
        if not project:
            raise HTTPException(status_code=404, detail={"success": False, "message": f"Project {project_id} not found."})
        return project

    def add_topics(self, project_id: int, topic_ids: List[int]):
        project = self.repo.add_topics(project_id, topic_ids)
        if not project:
            raise HTTPException(status_code=404, detail={"success": False, "message": f"Project {project_id} not found."})
        return project

    def get_user_projects(self, user_id: int) -> List:
        return self.repo.get_by_user_id(user_id)

    def get_project(self, project_id: int):
        project = self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail={"success": False, "message": f"Project {project_id} not found."})
        return project
