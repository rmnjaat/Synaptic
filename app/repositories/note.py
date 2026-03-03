"""NoteRepository with user-scoped queries."""
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.note import Note


class NoteRepository(BaseRepository[Note]):
    def __init__(self, db: Session):
        super().__init__(Note, db)

    def get_by_topic_id(self, topic_id: int) -> List[Note]:
        return self.db.query(Note).filter(Note.topic_id == topic_id).all()

    def get_by_user_id(self, user_id: int) -> List[Note]:
        return self.db.query(Note).filter(Note.user_id == user_id).all()
