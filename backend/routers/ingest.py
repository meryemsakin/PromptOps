"""Trace ingestion routes — the core data pipeline entry point."""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.auth import get_project_id_from_key
from backend.models.trace import Trace
from backend.schemas import TraceCreate, TraceBatchCreate, TraceResponse, TraceListResponse
from backend.services import calculate_cost

router = APIRouter(prefix="/v1/traces", tags=["Traces"])


@router.post("", response_model=TraceResponse, status_code=201)
async def ingest_trace(
    data: TraceCreate,
    project_id: UUID = Depends(get_project_id_from_key),
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single LLM trace."""
    # Calculate cost if tokens are provided
    cost = None
    if data.prompt_tokens is not None and data.completion_tokens is not None:
        cost = calculate_cost(data.model, data.prompt_tokens, data.completion_tokens)

    # Calculate total tokens if not provided
    total_tokens = data.total_tokens
    if total_tokens is None and data.prompt_tokens and data.completion_tokens:
        total_tokens = data.prompt_tokens + data.completion_tokens

    trace = Trace(
        project_id=project_id,
        trace_id=data.trace_id,
        span_id=data.span_id,
        parent_span_id=data.parent_span_id,
        model=data.model,
        provider=data.provider,
        prompt=data.prompt,
        messages=data.messages,
        completion=data.completion,
        function_call=data.function_call,
        prompt_tokens=data.prompt_tokens,
        completion_tokens=data.completion_tokens,
        total_tokens=total_tokens,
        cost_usd=cost,
        latency_ms=data.latency_ms,
        time_to_first_token_ms=data.time_to_first_token_ms,
        status=data.status,
        error_message=data.error_message,
        status_code=data.status_code,
        cache_hit=data.cache_hit,
        metadata=data.metadata,
        environment=data.environment,
    )
    db.add(trace)
    await db.flush()
    await db.refresh(trace)
    return trace


@router.post("/batch", status_code=201)
async def ingest_batch(
    data: TraceBatchCreate,
    project_id: UUID = Depends(get_project_id_from_key),
    db: AsyncSession = Depends(get_db),
):
    """Ingest multiple traces at once."""
    created = 0
    for trace_data in data.traces:
        cost = None
        if trace_data.prompt_tokens is not None and trace_data.completion_tokens is not None:
            cost = calculate_cost(trace_data.model, trace_data.prompt_tokens, trace_data.completion_tokens)

        total_tokens = trace_data.total_tokens
        if total_tokens is None and trace_data.prompt_tokens and trace_data.completion_tokens:
            total_tokens = trace_data.prompt_tokens + trace_data.completion_tokens

        trace = Trace(
            project_id=project_id,
            model=trace_data.model,
            provider=trace_data.provider,
            prompt=trace_data.prompt,
            messages=trace_data.messages,
            completion=trace_data.completion,
            prompt_tokens=trace_data.prompt_tokens,
            completion_tokens=trace_data.completion_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            latency_ms=trace_data.latency_ms,
            status=trace_data.status,
            error_message=trace_data.error_message,
            cache_hit=trace_data.cache_hit,
            metadata=trace_data.metadata,
            environment=trace_data.environment,
        )
        db.add(trace)
        created += 1

    await db.flush()
    return {"created": created}


@router.get("", response_model=TraceListResponse)
async def list_traces(
    project_id: UUID = Depends(get_project_id_from_key),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    model: Optional[str] = None,
    status: Optional[str] = None,
    environment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List traces with pagination and filtering."""
    query = select(Trace).where(Trace.project_id == project_id)

    if model:
        query = query.where(Trace.model == model)
    if status:
        query = query.where(Trace.status == status)
    if environment:
        query = query.where(Trace.environment == environment)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginated results
    query = query.order_by(Trace.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    traces = result.scalars().all()

    return TraceListResponse(
        traces=[TraceResponse.model_validate(t) for t in traces],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: UUID,
    project_id: UUID = Depends(get_project_id_from_key),
    db: AsyncSession = Depends(get_db),
):
    """Get a single trace by ID."""
    result = await db.execute(
        select(Trace).where(Trace.id == trace_id, Trace.project_id == project_id)
    )
    trace = result.scalar_one_or_none()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace
