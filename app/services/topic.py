"""TopicService — fully dynamic categories, no hardcoded enum."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.repositories.topic import TopicRepository
from app.models.topic import StatusEnum

# Fancy display names for the built-in categories (pure UI hint; not enforced)
CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    "backend":            "⚙️ Engine Room",
    "system_design":      "🏗️ Architecture Lab",
    "dsa":                "🧮 Algorithm Forge",
    "frontend":           "🎨 Pixel Craft",
    "devops":             "🚢 Launch Station",
    "database_design":    "🗄️ Data Vault",
    "projects_portfolio": "💎 Masterworks",
    "other":              "🌀 Open Realm",
}


def _display_name(cat: str) -> str:
    """Return a pretty display name; fall back to title-cased category key."""
    return CATEGORY_DISPLAY_NAMES.get(cat, cat.replace("_", " ").title())


class TopicService:
    def __init__(self, repo: TopicRepository):
        self.repo = repo

    def create_topic(self, topic_data: dict):
        """Create a topic — category is any non-empty string."""
        existing = self.repo.find_by_name_and_category(
            topic_data["user_id"], topic_data["name"], topic_data["category"]
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "data": None,
                    "message": "A topic with this name already exists in the selected category.",
                    "error": {"code": "DUPLICATE_TOPIC", "details": None},
                },
            )
        topic_data.setdefault("status", StatusEnum.to_learn)
        topic_data.setdefault("progress_percentage", 0.0)
        return self.repo.create(topic_data)

    def mark_completed(self, topic_id: int):
        self._require_topic(topic_id)
        # Cascade to subtopics if any exist
        from app.models.subtopic import SubTopic
        self.repo.db.query(SubTopic).filter(SubTopic.topic_id == topic_id).update({
            "status": StatusEnum.completed,
            "completed_at": datetime.now(timezone.utc).replace(tzinfo=None),
            "updated_at": datetime.now(timezone.utc).replace(tzinfo=None)
        })
        return self.repo.update(topic_id, {
            "status": StatusEnum.completed,
            "progress_percentage": 100.0,
            "completed_at": datetime.now(timezone.utc).replace(tzinfo=None),
        })

    def mark_in_progress(self, topic_id: int):
        self._require_topic(topic_id)
        # We don't necessarily force subtopics to in-progress here, 
        # as the user might want to pick which one to start.
        return self.repo.update(topic_id, {"status": StatusEnum.in_progress, "completed_at": None})

    def mark_to_learn(self, topic_id: int):
        self._require_topic(topic_id)
        # Cascade to subtopics: reset all to to-learn
        from app.models.subtopic import SubTopic
        self.repo.db.query(SubTopic).filter(SubTopic.topic_id == topic_id).update({
            "status": StatusEnum.to_learn,
            "completed_at": None,
            "updated_at": datetime.now(timezone.utc).replace(tzinfo=None)
        })
        return self.repo.update(topic_id, {
            "status": StatusEnum.to_learn,
            "progress_percentage": 0.0,
            "completed_at": None
        })

    def get_topic(self, topic_id: int):
        return self._require_topic(topic_id)

    def get_user_topics(self, user_id: int) -> Dict[str, Any]:
        """Return all topics grouped by their actual category string."""
        topics = self.repo.get_by_user_id(user_id)
        grouped: Dict[str, list] = {}
        for t in topics:
            grouped.setdefault(t.category, []).append(t)
        return {"user_id": user_id, "topics_by_category": grouped}

    def get_user_category_progress(self, user_id: int, category: str) -> Dict[str, Any]:
        """Return progress stats for any category string."""
        return self.repo.get_category_progress(user_id, category)

    def get_overall_progress(self, user_id: int) -> Dict[str, Any]:
        """Dynamically compute progress across every category the user has topics in."""
        cats = self.repo.get_distinct_categories(user_id)
        categories_data: Dict[str, Any] = {}
        total_progress = 0.0

        for cat in cats:
            stats = self.repo.get_category_progress(user_id, cat)
            display = _display_name(cat)
            categories_data[display] = {**stats, "category_key": cat}
            total_progress += stats["progress_percentage"]

        overall = round(total_progress / len(cats), 2) if cats else 0.0
        return {"user_id": user_id, "overall_progress": overall, "categories": categories_data}

    # ── helpers ───────────────────────────────────────────────────────────────
    def _require_topic(self, topic_id: int):
        topic = self.repo.get_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "data": None,
                    "message": f"Topic {topic_id} not found.",
                    "error": {"code": "TOPIC_NOT_FOUND", "details": None},
                },
            )
        return topic
