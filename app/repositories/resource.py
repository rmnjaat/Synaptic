"""ResourceRepository."""
from typing import List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.resource import Resource


class ResourceRepository(BaseRepository[Resource]):
    def __init__(self, db: Session):
        super().__init__(Resource, db)

    def get_by_topic_id(self, topic_id: int) -> List[Resource]:
        return self.db.query(Resource).filter(Resource.topic_id == topic_id).all()
