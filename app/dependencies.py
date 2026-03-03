"""FastAPI dependency injection wiring for all services."""
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.repositories.topic import TopicRepository
from app.repositories.subtopic import SubTopicRepository
from app.repositories.note import NoteRepository
from app.repositories.resource import ResourceRepository
from app.repositories.project import ProjectRepository
from app.repositories.search import SearchRepository
from app.services.topic import TopicService
from app.services.subtopic import SubTopicService
from app.services.note import NoteService
from app.services.project import ProjectService
from app.services.search import SearchService


def get_topic_service(db: Session = Depends(get_db)) -> TopicService:
    return TopicService(TopicRepository(db))


def get_subtopic_service(db: Session = Depends(get_db)) -> SubTopicService:
    return SubTopicService(SubTopicRepository(db), TopicRepository(db))


def get_note_service(db: Session = Depends(get_db)) -> NoteService:
    return NoteService(NoteRepository(db))


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db))


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    return SearchService(SearchRepository(db))
