"""LLM request trace model — the core data unit of the platform."""

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import Base, UUIDMixin, TimestampMixin


class Trace(Base, UUIDMixin, TimestampMixin):
    """A single LLM API call record with full request/response data."""

    __tablename__ = "traces"

    # Project association
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    # Request metadata
    trace_id = Column(String(255), nullable=True, index=True)  # External trace ID for grouping
    span_id = Column(String(255), nullable=True)  # Span within a trace
    parent_span_id = Column(String(255), nullable=True)

    # LLM call details
    model = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False, default="openai")  # openai, anthropic, etc.

    # Input/Output
    prompt = Column(Text, nullable=True)  # Raw prompt or last user message
    messages = Column(JSON, nullable=True)  # Full messages array for chat models
    completion = Column(Text, nullable=True)  # Model response
    function_call = Column(JSON, nullable=True)  # Tool/function call if any

    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    # Cost (calculated)
    cost_usd = Column(Float, nullable=True)

    # Performance
    latency_ms = Column(Float, nullable=True)  # End-to-end latency
    time_to_first_token_ms = Column(Float, nullable=True)  # Streaming TTFT

    # Status
    status = Column(String(20), nullable=False, default="success")  # success, error, timeout
    error_message = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)

    # Cache
    cache_hit = Column(Boolean, default=False, nullable=False)
    cache_key = Column(String(255), nullable=True)

    # Custom metadata
    metadata = Column(JSON, nullable=True)  # User-defined tags, labels, etc.
    environment = Column(String(50), nullable=True, default="production")  # production, staging, dev

    # Relationships
    project = relationship("Project", back_populates="traces")
    eval_results = relationship("EvalResult", back_populates="trace", cascade="all, delete-orphan")

    # Indexes for analytics queries
    __table_args__ = (
        Index("ix_traces_project_created", "project_id", "created_at"),
        Index("ix_traces_model_created", "model", "created_at"),
        Index("ix_traces_status", "status"),
    )

    def __repr__(self):
        return f"<Trace(id={self.id}, model='{self.model}', cost=${self.cost_usd:.4f})>"
