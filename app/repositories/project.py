"""ProjectRepository with topic association management."""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.project import Project, ProjectStatusEnum
from app.models.topic import Topic


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)

    def get_by_user_id(self, user_id: int) -> List[Project]:
        return self.db.query(Project).filter(Project.user_id == user_id).all()

    def mark_completed(self, project_id: int) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        project.status = ProjectStatusEnum.completed
        project.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        project.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(project)
        return project

    def add_topics(self, project_id: int, topic_ids: List[int]) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        for topic_id in topic_ids:
            topic = self.db.query(Topic).filter(Topic.id == topic_id).first()
            if topic and topic not in project.topics:
                project.topics.append(topic)
        self.db.commit()
        self.db.refresh(project)
        return project
