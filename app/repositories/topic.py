"""TopicRepository — category is now a plain string, all queries updated."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.repositories.base import BaseRepository
from app.models.topic import Topic, StatusEnum


class TopicRepository(BaseRepository[Topic]):
    def __init__(self, db: Session):
        super().__init__(Topic, db)

    def get_by_user_id(self, user_id: int) -> List[Topic]:
        return (
            self.db.query(Topic)
            .filter(Topic.user_id == user_id)
            .order_by(Topic.created_at.desc())
            .all()
        )

    def get_by_category(self, user_id: int, category: str) -> List[Topic]:
        return (
            self.db.query(Topic)
            .filter(Topic.user_id == user_id, Topic.category == category)
            .order_by(Topic.created_at.desc())
            .all()
        )

    def get_by_status(self, user_id: int, status: str) -> List[Topic]:
        return (
            self.db.query(Topic)
            .filter(Topic.user_id == user_id, Topic.status == status)
            .order_by(Topic.created_at.desc())
            .all()
        )

    def get_distinct_categories(self, user_id: int) -> List[str]:
        """Return every unique category string that this user has topics in."""
        rows = (
            self.db.query(distinct(Topic.category))
            .filter(Topic.user_id == user_id)
            .all()
        )
        return [r[0] for r in rows]

    def get_category_progress(self, user_id: int, category: str) -> Dict[str, Any]:
        topics   = self.get_by_category(user_id, category)
        total    = len(topics)
        completed   = sum(1 for t in topics if t.status == StatusEnum.completed)
        in_progress = sum(1 for t in topics if t.status == StatusEnum.in_progress)
        to_learn    = sum(1 for t in topics if t.status == StatusEnum.to_learn)
        progress    = round((completed / total) * 100, 2) if total > 0 else 0.0
        most_recent = topics[0] if topics else None
        return {
            "category": category,
            "total_topics": total,
            "completed": completed,
            "in_progress": in_progress,
            "to_learn": to_learn,
            "progress_percentage": progress,
            "most_recent_topic": most_recent.name if most_recent else None,
        }

    def update_progress_percentage(self, topic_id: int) -> Optional[Topic]:
        """Recalculate and persist progress based on subtopic completion."""
        from app.models.subtopic import SubTopic

        topic = self.get_by_id(topic_id)
        if not topic:
            return None

        subtopics = self.db.query(SubTopic).filter(SubTopic.topic_id == topic_id).all()
        total     = len(subtopics)
        completed = sum(1 for s in subtopics if s.status == StatusEnum.completed)

        topic.progress_percentage = round((completed / total) * 100, 2) if total > 0 else 0.0
        topic.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_topics_by_search(self, user_id: int, query: str) -> List[Topic]:
        pattern = f"%{query}%"
        return (
            self.db.query(Topic)
            .filter(
                Topic.user_id == user_id,
                (Topic.name.ilike(pattern)) | (Topic.description.ilike(pattern)),
            )
            .all()
        )

    def find_by_name_and_category(self, user_id: int, name: str, category: str) -> Optional[Topic]:
        return (
            self.db.query(Topic)
            .filter(
                Topic.user_id == user_id,
                Topic.name == name,
                Topic.category == category,
            )
            .first()
        )
