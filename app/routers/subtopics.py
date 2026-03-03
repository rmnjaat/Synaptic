"""SubTopics router — nested under topics and standalone."""
from fastapi import APIRouter, Depends, status
from app.schemas.subtopic import SubTopicCreate, SubTopicRead
from app.schemas.common import APIResponse
from app.services.subtopic import SubTopicService
from app.dependencies import get_subtopic_service
from typing import List

router = APIRouter(tags=["SubTopics"])


@router.post(
    "/topics/{topic_id}/subtopics/create",
    response_model=APIResponse[SubTopicRead],
    status_code=status.HTTP_201_CREATED,
)
def create_subtopic(
    topic_id: int,
    payload: SubTopicCreate,
    svc: SubTopicService = Depends(get_subtopic_service),
):
    """Create a sub-topic under a topic."""
    st = svc.create_subtopic(topic_id, payload.model_dump())
    return APIResponse.ok(data=SubTopicRead.model_validate(st), message="SubTopic created.")


@router.get("/topics/{topic_id}/subtopics", response_model=APIResponse[List[SubTopicRead]])
def get_subtopics(topic_id: int, svc: SubTopicService = Depends(get_subtopic_service)):
    """Get all sub-topics for a topic."""
    sts = svc.get_subtopics(topic_id)
    return APIResponse.ok(data=[SubTopicRead.model_validate(s) for s in sts])


@router.post("/subtopics/{subtopic_id}/mark-completed", response_model=APIResponse[SubTopicRead])
def mark_subtopic_completed(subtopic_id: int, svc: SubTopicService = Depends(get_subtopic_service)):
    """Mark a sub-topic as completed and cascade progress update."""
    st = svc.mark_completed(subtopic_id)
    return APIResponse.ok(data=SubTopicRead.model_validate(st), message="SubTopic marked as completed.")


@router.post("/subtopics/{subtopic_id}/mark-in-progress", response_model=APIResponse[SubTopicRead])
def mark_subtopic_in_progress(subtopic_id: int, svc: SubTopicService = Depends(get_subtopic_service)):
    """Mark a sub-topic as in-progress."""
    st = svc.mark_in_progress(subtopic_id)
    return APIResponse.ok(data=SubTopicRead.model_validate(st), message="SubTopic marked as in-progress.")


@router.post("/subtopics/{subtopic_id}/mark-to-learn", response_model=APIResponse[SubTopicRead])
def mark_subtopic_to_learn(subtopic_id: int, svc: SubTopicService = Depends(get_subtopic_service)):
    """Reset a sub-topic status to to-learn."""
    st = svc.mark_to_learn(subtopic_id)
    return APIResponse.ok(data=SubTopicRead.model_validate(st), message="SubTopic marked as to-learn.")


@router.delete("/subtopics/{subtopic_id}", response_model=APIResponse[None])
def delete_subtopic(subtopic_id: int, svc: SubTopicService = Depends(get_subtopic_service)):
    """Delete a sub-topic and update parent progress."""
    svc.delete_subtopic(subtopic_id)
    return APIResponse.ok(message="SubTopic deleted.")
