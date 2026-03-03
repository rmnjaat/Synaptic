"""Resource SQLAlchemy model."""
import enum
from datetime import datetime
from sqlalchemy import String, Enum as SAEnum, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ResourceTypeEnum(str, enum.Enum):
    link = "link"
    book = "book"
    course = "course"
    video = "video"
    article = "article"


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=True)
    resource_type: Mapped[str] = mapped_column(SAEnum(ResourceTypeEnum), default=ResourceTypeEnum.link)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="resources")
