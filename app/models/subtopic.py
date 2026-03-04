"""SubTopic SQLAlchemy model."""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.topic import StatusEnum


class SubTopic(Base):
    __tablename__ = "subtopics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(1000), nullable=True)
    links: Mapped[str] = mapped_column(Text, nullable=True)  # JSON: [{"label":"...","url":"..."}]
    status: Mapped[str] = mapped_column(SAEnum(StatusEnum), default=StatusEnum.to_learn, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="subtopics")
