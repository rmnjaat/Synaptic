"""SubTopicService — business logic with cascade progress updates."""
from typing import List
from fastapi import HTTPException
from app.repositories.subtopic import SubTopicRepository
from app.repositories.topic import TopicRepository


class SubTopicService:
    def __init__(self, repo: SubTopicRepository, topic_repo: TopicRepository):
        self.repo = repo
        self.topic_repo = topic_repo

    def create_subtopic(self, topic_id: int, subtopic_data: dict):
        topic = self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail=self._not_found_resp("Topic", topic_id))
        existing = self.repo.find_by_name_in_topic(topic_id, subtopic_data["name"])
        if existing:
            raise HTTPException(
                status_code=409,
                detail={
                    "success": False,
                    "data": None,
                    "message": "A sub-topic with this name already exists in this topic.",
                    "error": {"code": "DUPLICATE_SUBTOPIC", "details": None},
                },
            )
        subtopic_data["topic_id"] = topic_id
        st = self.repo.create(subtopic_data)
        self.topic_repo.update_progress_percentage(topic_id)
        return st

    def get_subtopics(self, topic_id: int) -> List:
        topic = self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail=self._not_found_resp("Topic", topic_id))
        return self.repo.get_by_topic_id(topic_id)

    def mark_completed(self, subtopic_id: int):
        st = self.repo.mark_completed(subtopic_id)
        if not st:
            raise HTTPException(status_code=404, detail=self._not_found_resp("SubTopic", subtopic_id))
        self.topic_repo.update_progress_percentage(st.topic_id)
        return st

    def mark_in_progress(self, subtopic_id: int):
        st = self.repo.mark_in_progress(subtopic_id)
        if not st:
            raise HTTPException(status_code=404, detail=self._not_found_resp("SubTopic", subtopic_id))
        self.topic_repo.update_progress_percentage(st.topic_id)
        return st

    def mark_to_learn(self, subtopic_id: int):
        st = self.repo.mark_to_learn(subtopic_id)
        if not st:
            raise HTTPException(status_code=404, detail=self._not_found_resp("SubTopic", subtopic_id))
        self.topic_repo.update_progress_percentage(st.topic_id)
        return st

    def delete_subtopic(self, subtopic_id: int) -> bool:
        st = self.repo.get_by_id(subtopic_id)
        if not st:
            raise HTTPException(status_code=404, detail=self._not_found_resp("SubTopic", subtopic_id))
        topic_id = st.topic_id
        self.repo.delete(subtopic_id)
        self.topic_repo.update_progress_percentage(topic_id)
        return True

    def _not_found_resp(self, entity: str, id: int) -> dict:
        return {
            "success": False,
            "data": None,
            "message": f"{entity} {id} not found.",
            "error": {"code": f"{entity.upper()}_NOT_FOUND", "details": None},
        }
