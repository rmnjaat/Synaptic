"""Generic base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.database import Base
from app.services.gdrive_sync import mark_modified

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        mark_modified()
        return db_obj

    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        for key, value in obj_in.items():
            if value is not None or key in obj_in:
                setattr(db_obj, key, value)
        self.db.commit()
        self.db.refresh(db_obj)
        mark_modified()
        return db_obj

    def delete(self, id: int) -> bool:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        self.db.delete(db_obj)
        self.db.commit()
        mark_modified()
        return True
