"""Project and project_topics association table models."""
import enum
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Table, Column, Integer, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProjectStatusEnum(str, enum.Enum):
    planning = "planning"
    in_progress = "in-progress"
    completed = "completed"
    on_hold = "on-hold"


# Many-to-many association table
project_topics = Table(
    "project_topics",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[str] = mapped_column(Text, nullable=True)  # JSON or comma-separated
    github_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    live_demo_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(SAEnum(ProjectStatusEnum), default=ProjectStatusEnum.planning)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="projects")
    topics = relationship("Topic", secondary=project_topics, backref="projects")
