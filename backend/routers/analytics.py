"""Analytics API routes — cost, latency, usage, errors, overview."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.database import get_db
from backend.auth import get_project_id_from_key
from backend.schemas import CostSummary, LatencySummary, UsageSummary, ErrorSummary, OverviewSummary
from backend.services.analytics_engine import (
    get_cost_summary,
    get_latency_summary,
    get_usage_summary,
    get_error_summary,
    get_overview,
)

router = APIRouter(prefix="/v1/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewSummary)
async def analytics_overview(
    days: int = Query(30, ge=1, le=365),
    project_id: UUID = Depends(get_project_id_from_key),
    db=Depends(get_db),
):
    """Get dashboard overview with key metrics."""
    return await get_overview(db, project_id, days)


@router.get("/cost", response_model=CostSummary)
async def analytics_cost(
    days: int = Query(30, ge=1, le=365),
    project_id: UUID = Depends(get_project_id_from_key),
    db=Depends(get_db),
):
    """Get cost analytics — total, per-model, daily breakdown."""
    return await get_cost_summary(db, project_id, days)


@router.get("/latency", response_model=LatencySummary)
async def analytics_latency(
    days: int = Query(30, ge=1, le=365),
    project_id: UUID = Depends(get_project_id_from_key),
    db=Depends(get_db),
):
    """Get latency percentiles — avg, p50, p95, p99."""
    return await get_latency_summary(db, project_id, days)


@router.get("/usage", response_model=UsageSummary)
async def analytics_usage(
    days: int = Query(30, ge=1, le=365),
    project_id: UUID = Depends(get_project_id_from_key),
    db=Depends(get_db),
):
    """Get usage stats — requests, tokens, models, statuses."""
    return await get_usage_summary(db, project_id, days)


@router.get("/errors", response_model=ErrorSummary)
async def analytics_errors(
    days: int = Query(30, ge=1, le=365),
    project_id: UUID = Depends(get_project_id_from_key),
    db=Depends(get_db),
):
    """Get error analytics — rate, types, recent errors."""
    return await get_error_summary(db, project_id, days)
