"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ── Project Schemas ──────────────────────────────────────────

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class APIKeyCreate(BaseModel):
    name: str = Field(default="Default", max_length=255)


class APIKeyResponse(BaseModel):
    id: UUID
    key_prefix: str
    name: str
    is_active: bool
    created_at: datetime
    # Full key only returned on creation
    full_key: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Trace Schemas ────────────────────────────────────────────

class TraceCreate(BaseModel):
    """Schema for ingesting a single LLM trace."""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    model: str
    provider: str = "openai"

    prompt: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    completion: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    latency_ms: Optional[float] = None
    time_to_first_token_ms: Optional[float] = None

    status: str = "success"
    error_message: Optional[str] = None
    status_code: Optional[int] = None

    cache_hit: bool = False

    metadata: Optional[Dict[str, Any]] = None
    environment: Optional[str] = "production"


class TraceBatchCreate(BaseModel):
    """Schema for ingesting multiple traces at once."""
    traces: List[TraceCreate]


class TraceResponse(BaseModel):
    id: UUID
    project_id: UUID
    trace_id: Optional[str]
    model: str
    provider: str
    prompt: Optional[str]
    completion: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    cost_usd: Optional[float]
    latency_ms: Optional[float]
    status: str
    error_message: Optional[str]
    cache_hit: bool
    metadata: Optional[Dict[str, Any]]
    environment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceListResponse(BaseModel):
    traces: List[TraceResponse]
    total: int
    page: int
    page_size: int


# ── Analytics Schemas ────────────────────────────────────────

class CostSummary(BaseModel):
    total_cost_usd: float
    total_requests: int
    avg_cost_per_request: float
    cost_by_model: Dict[str, float]
    daily_costs: List[Dict[str, Any]]


class LatencySummary(BaseModel):
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    daily_latency: List[Dict[str, Any]]


class UsageSummary(BaseModel):
    total_requests: int
    total_tokens: int
    requests_by_model: Dict[str, int]
    requests_by_status: Dict[str, int]
    daily_requests: List[Dict[str, Any]]


class ErrorSummary(BaseModel):
    total_errors: int
    error_rate: float
    errors_by_type: Dict[str, int]
    recent_errors: List[Dict[str, Any]]


class CacheSummary(BaseModel):
    total_lookups: int
    cache_hits: int
    hit_rate: float
    total_tokens_saved: int
    total_cost_saved_usd: float


class OverviewSummary(BaseModel):
    """Dashboard overview combining key metrics."""
    total_requests: int
    total_cost_usd: float
    avg_latency_ms: float
    error_rate: float
    cache_hit_rate: float
    cost_saved_usd: float
    total_tokens: int
    active_models: List[str]


# ── Eval Schemas ─────────────────────────────────────────────

class EvalResultCreate(BaseModel):
    trace_id: UUID
    eval_type: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None
    ground_truth: Optional[str] = None
    eval_metadata: Optional[Dict[str, Any]] = None


class EvalResultResponse(BaseModel):
    id: UUID
    trace_id: UUID
    eval_type: str
    score: float
    passed: Optional[str]
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
