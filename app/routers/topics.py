"""Topics router."""
from fastapi import APIRouter, Depends, status
from app.schemas.topic import TopicCreate, TopicDetailRead, TopicRead
from app.schemas.common import APIResponse
from app.services.topic import TopicService
from app.dependencies import get_topic_service

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post("/create", response_model=APIResponse[TopicRead], status_code=status.HTTP_201_CREATED)
def create_topic(payload: TopicCreate, svc: TopicService = Depends(get_topic_service)):
    """Create a new learning topic."""
    topic = svc.create_topic(payload.model_dump())
    return APIResponse.ok(data=TopicRead.model_validate(topic), message="Topic created successfully.")


@router.get("/{topic_id}", response_model=APIResponse[TopicDetailRead])
def get_topic(topic_id: int, svc: TopicService = Depends(get_topic_service)):
    """Retrieve a topic with its subtopics, notes, and resources."""
    topic = svc.get_topic(topic_id)
    return APIResponse.ok(data=TopicDetailRead.model_validate(topic))


@router.post("/{topic_id}/mark-completed", response_model=APIResponse[TopicRead])
def mark_topic_completed(topic_id: int, svc: TopicService = Depends(get_topic_service)):
    """Mark a topic as completed."""
    topic = svc.mark_completed(topic_id)
    return APIResponse.ok(data=TopicRead.model_validate(topic), message="Topic marked as completed.")


@router.post("/{topic_id}/mark-in-progress", response_model=APIResponse[TopicRead])
def mark_topic_in_progress(topic_id: int, svc: TopicService = Depends(get_topic_service)):
    """Mark a topic as in-progress."""
    topic = svc.mark_in_progress(topic_id)
    return APIResponse.ok(data=TopicRead.model_validate(topic), message="Topic marked as in-progress.")


@router.post("/{topic_id}/mark-to-learn", response_model=APIResponse[TopicRead])
def mark_topic_to_learn(topic_id: int, svc: TopicService = Depends(get_topic_service)):
    """Reset a topic status to to-learn."""
    topic = svc.mark_to_learn(topic_id)
    return APIResponse.ok(data=TopicRead.model_validate(topic), message="Topic marked as to-learn.")
