"""SearchRepository for case-insensitive cross-entity global search."""
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.topic import Topic
from app.models.subtopic import SubTopic
from app.models.note import Note
from app.models.project import Project


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_all(self, user_id: int, query: str) -> Dict[str, Any]:
        pattern = f"%{query}%"

        topics = (
            self.db.query(Topic)
            .filter(
                Topic.user_id == user_id,
                (Topic.name.ilike(pattern)) | (Topic.description.ilike(pattern)),
            )
            .all()
        )

        # SubTopic doesn't have user_id; join through topics
        subtopics = (
            self.db.query(SubTopic)
            .join(Topic, SubTopic.topic_id == Topic.id)
            .filter(Topic.user_id == user_id, SubTopic.name.ilike(pattern))
            .all()
        )

        notes = (
            self.db.query(Note)
            .filter(
                Note.user_id == user_id,
                (Note.title.ilike(pattern)) | (Note.content.ilike(pattern)),
            )
            .all()
        )

        projects = (
            self.db.query(Project)
            .filter(
                Project.user_id == user_id,
                (Project.name.ilike(pattern)) | (Project.description.ilike(pattern)),
            )
            .all()
        )

        return {
            "topics": topics,
            "sub_topics": subtopics,
            "notes": notes,
            "projects": projects,
        }
