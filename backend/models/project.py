"""Project and API Key models."""

import secrets
from sqlalchemy import Column, String, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import Base, UUIDMixin, TimestampMixin
from backend.config import settings


class Project(Base, UUIDMixin, TimestampMixin):
    """A project that groups LLM traces together."""

    __tablename__ = "projects"

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    api_keys = relationship("APIKey", back_populates="project", cascade="all, delete-orphan")
    traces = relationship("Trace", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class APIKey(Base, UUIDMixin, TimestampMixin):
    """API key for authenticating SDK requests to a project."""

    __tablename__ = "api_keys"

    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    key_prefix = Column(String(20), nullable=False)  # First 8 chars for identification
    name = Column(String(255), nullable=False, default="Default")
    is_active = Column(Boolean, default=True, nullable=False)

    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="api_keys")

    @staticmethod
    def generate_key() -> str:
        """Generate a new API key with the configured prefix."""
        random_part = secrets.token_urlsafe(32)
        return f"{settings.API_KEY_PREFIX}{random_part}"

    def __repr__(self):
        return f"<APIKey(id={self.id}, prefix='{self.key_prefix}')>"
