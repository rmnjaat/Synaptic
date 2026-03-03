"""SubTopicRepository with status management methods."""
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.subtopic import SubTopic
from app.models.topic import StatusEnum


class SubTopicRepository(BaseRepository[SubTopic]):
    def __init__(self, db: Session):
        super().__init__(SubTopic, db)

    def get_by_topic_id(self, topic_id: int) -> List[SubTopic]:
        return (
            self.db.query(SubTopic)
            .filter(SubTopic.topic_id == topic_id)
            .order_by(SubTopic.order_index.asc(), SubTopic.created_at.asc())
            .all()
        )

    def find_by_name_in_topic(self, topic_id: int, name: str) -> Optional[SubTopic]:
        return (
            self.db.query(SubTopic)
            .filter(SubTopic.topic_id == topic_id, SubTopic.name == name)
            .first()
        )

    def mark_completed(self, subtopic_id: int) -> Optional[SubTopic]:
        st = self.get_by_id(subtopic_id)
        if not st:
            return None
        st.status = StatusEnum.completed
        st.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        st.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(st)
        return st

    def mark_in_progress(self, subtopic_id: int) -> Optional[SubTopic]:
        st = self.get_by_id(subtopic_id)
        if not st:
            return None
        st.status = StatusEnum.in_progress
        st.completed_at = None
        st.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(st)
        return st

    def mark_to_learn(self, subtopic_id: int) -> Optional[SubTopic]:
        st = self.get_by_id(subtopic_id)
        if not st:
            return None
        st.status = StatusEnum.to_learn
        st.completed_at = None
        st.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.db.commit()
        self.db.refresh(st)
        return st

    def update_topic_progress(self, topic_id: int) -> None:
        """Delegate progress recalculation to TopicRepository."""
        from app.repositories.topic import TopicRepository
        topic_repo = TopicRepository(self.db)
        topic_repo.update_progress_percentage(topic_id)
