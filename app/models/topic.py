"""Topic SQLAlchemy model.

Category is now a free-form String — any custom category name is accepted.
StatusEnum is still enforced (to-learn / in-progress / completed are meaningful states).
"""
import enum
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Enum as SAEnum, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# Status remains a controlled enum — there are only 3 meaningful states
class StatusEnum(str, enum.Enum):
    to_learn   = "to-learn"
    in_progress = "in-progress"
    completed  = "completed"


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int]   = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str]  = mapped_column(String(1000), nullable=True)

    # ← FREE-FORM string — no enum constraint; accepts any category name
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    status: Mapped[str] = mapped_column(SAEnum(StatusEnum), default=StatusEnum.to_learn, index=True)
    parent_topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=True)
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    order_index: Mapped[int]  = mapped_column(Integer, default=0)
    is_public: Mapped[bool]   = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    user      = relationship("User",     back_populates="topics")
    subtopics = relationship("SubTopic", back_populates="topic", cascade="all, delete-orphan")
    notes     = relationship("Note",     back_populates="topic", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_topics_user_category", "user_id", "category"),
        Index("ix_topics_user_status",   "user_id", "status"),
    )
