"""Evaluation result model — quality scores for individual traces."""

from sqlalchemy import Column, String, Float, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.models.base import Base, UUIDMixin, TimestampMixin


class EvalResult(Base, UUIDMixin, TimestampMixin):
    """Quality evaluation result for a single trace."""

    __tablename__ = "eval_results"

    # Trace association
    trace_id = Column(UUID(as_uuid=True), ForeignKey("traces.id"), nullable=False)

    # Evaluation type
    eval_type = Column(String(50), nullable=False)  # hallucination, relevance, groundedness, custom

    # Scores
    score = Column(Float, nullable=False)  # 0.0 - 1.0
    passed = Column(String(10), nullable=True)  # pass, fail, warning

    # Details
    reason = Column(Text, nullable=True)  # Explanation of the score
    ground_truth = Column(Text, nullable=True)  # Expected answer (if available)
    eval_metadata = Column(JSON, nullable=True)  # Extra eval data

    # Relationships
    trace = relationship("Trace", back_populates="eval_results")

    def __repr__(self):
        return f"<EvalResult(trace={self.trace_id}, type='{self.eval_type}', score={self.score:.2f})>"
