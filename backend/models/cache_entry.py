"""Semantic cache entry model with vector embedding."""

from sqlalchemy import Column, String, Text, Float, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from backend.models.base import Base, UUIDMixin, TimestampMixin
from backend.config import settings


class CacheEntry(Base, UUIDMixin, TimestampMixin):
    """Cached LLM response with semantic embedding for similarity lookup."""

    __tablename__ = "cache_entries"

    # Project association
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Cache content
    prompt_text = Column(Text, nullable=False)  # Original prompt
    response_text = Column(Text, nullable=False)  # Cached response
    model = Column(String(100), nullable=False)

    # Vector embedding for semantic search
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)

    # Stats
    hit_count = Column(Integer, default=0, nullable=False)
    tokens_saved = Column(Integer, default=0, nullable=False)
    cost_saved_usd = Column(Float, default=0.0, nullable=False)

    # Metadata
    cache_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<CacheEntry(id={self.id}, hits={self.hit_count})>"
