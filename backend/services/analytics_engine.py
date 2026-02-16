"""Analytics engine — aggregation queries for the dashboard."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, case, text, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.trace import Trace


async def get_cost_summary(
    db: AsyncSession,
    project_id: UUID,
    days: int = 30,
) -> dict:
    """Get cost analytics for a project over the specified period."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Total cost and request count
    result = await db.execute(
        select(
            func.coalesce(func.sum(Trace.cost_usd), 0).label("total_cost"),
            func.count(Trace.id).label("total_requests"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        )
    )
    row = result.one()
    total_cost = float(row.total_cost)
    total_requests = int(row.total_requests)

    # Cost by model
    model_result = await db.execute(
        select(
            Trace.model,
            func.coalesce(func.sum(Trace.cost_usd), 0).label("cost"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).group_by(Trace.model)
    )
    cost_by_model = {r.model: round(float(r.cost), 4) for r in model_result.all()}

    # Daily costs
    daily_result = await db.execute(
        select(
            func.date_trunc("day", Trace.created_at).label("day"),
            func.coalesce(func.sum(Trace.cost_usd), 0).label("cost"),
            func.count(Trace.id).label("requests"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).group_by(text("day")).order_by(text("day"))
    )
    daily_costs = [
        {
            "date": r.day.isoformat() if r.day else None,
            "cost": round(float(r.cost), 4),
            "requests": int(r.requests),
        }
        for r in daily_result.all()
    ]

    return {
        "total_cost_usd": round(total_cost, 4),
        "total_requests": total_requests,
        "avg_cost_per_request": round(total_cost / total_requests, 6) if total_requests > 0 else 0,
        "cost_by_model": cost_by_model,
        "daily_costs": daily_costs,
    }


async def get_latency_summary(
    db: AsyncSession,
    project_id: UUID,
    days: int = 30,
) -> dict:
    """Get latency percentiles for a project."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Get all latency values
    result = await db.execute(
        select(Trace.latency_ms).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
            Trace.latency_ms.isnot(None),
        ).order_by(Trace.latency_ms)
    )
    latencies = [float(r.latency_ms) for r in result.all()]

    if not latencies:
        return {
            "avg_latency_ms": 0,
            "p50_latency_ms": 0,
            "p95_latency_ms": 0,
            "p99_latency_ms": 0,
            "daily_latency": [],
        }

    n = len(latencies)
    avg_lat = sum(latencies) / n
    p50 = latencies[int(n * 0.50)]
    p95 = latencies[int(min(n * 0.95, n - 1))]
    p99 = latencies[int(min(n * 0.99, n - 1))]

    # Daily avg latency
    daily_result = await db.execute(
        select(
            func.date_trunc("day", Trace.created_at).label("day"),
            func.avg(Trace.latency_ms).label("avg_latency"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
            Trace.latency_ms.isnot(None),
        ).group_by(text("day")).order_by(text("day"))
    )
    daily_latency = [
        {
            "date": r.day.isoformat() if r.day else None,
            "avg_latency_ms": round(float(r.avg_latency), 2),
        }
        for r in daily_result.all()
    ]

    return {
        "avg_latency_ms": round(avg_lat, 2),
        "p50_latency_ms": round(p50, 2),
        "p95_latency_ms": round(p95, 2),
        "p99_latency_ms": round(p99, 2),
        "daily_latency": daily_latency,
    }


async def get_usage_summary(
    db: AsyncSession,
    project_id: UUID,
    days: int = 30,
) -> dict:
    """Get usage statistics — requests, tokens, models."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Totals
    result = await db.execute(
        select(
            func.count(Trace.id).label("total_requests"),
            func.coalesce(func.sum(Trace.total_tokens), 0).label("total_tokens"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        )
    )
    row = result.one()

    # By model
    model_result = await db.execute(
        select(
            Trace.model,
            func.count(Trace.id).label("count"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).group_by(Trace.model)
    )
    requests_by_model = {r.model: int(r.count) for r in model_result.all()}

    # By status
    status_result = await db.execute(
        select(
            Trace.status,
            func.count(Trace.id).label("count"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).group_by(Trace.status)
    )
    requests_by_status = {r.status: int(r.count) for r in status_result.all()}

    # Daily requests
    daily_result = await db.execute(
        select(
            func.date_trunc("day", Trace.created_at).label("day"),
            func.count(Trace.id).label("requests"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).group_by(text("day")).order_by(text("day"))
    )
    daily_requests = [
        {
            "date": r.day.isoformat() if r.day else None,
            "requests": int(r.requests),
        }
        for r in daily_result.all()
    ]

    return {
        "total_requests": int(row.total_requests),
        "total_tokens": int(row.total_tokens),
        "requests_by_model": requests_by_model,
        "requests_by_status": requests_by_status,
        "daily_requests": daily_requests,
    }


async def get_error_summary(
    db: AsyncSession,
    project_id: UUID,
    days: int = 30,
) -> dict:
    """Get error analytics."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Total errors
    result = await db.execute(
        select(
            func.count(Trace.id).label("total"),
            func.sum(case((Trace.status == "error", 1), else_=0)).label("errors"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        )
    )
    row = result.one()
    total = int(row.total) if row.total else 0
    errors = int(row.errors) if row.errors else 0

    # Recent errors
    error_result = await db.execute(
        select(Trace).where(
            Trace.project_id == project_id,
            Trace.status == "error",
            Trace.created_at >= since,
        ).order_by(Trace.created_at.desc()).limit(20)
    )
    recent_errors = [
        {
            "id": str(t.id),
            "model": t.model,
            "error_message": t.error_message,
            "status_code": t.status_code,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in error_result.scalars().all()
    ]

    return {
        "total_errors": errors,
        "error_rate": round(errors / total, 4) if total > 0 else 0,
        "errors_by_type": {},  # Would need error classification
        "recent_errors": recent_errors,
    }


async def get_overview(
    db: AsyncSession,
    project_id: UUID,
    days: int = 30,
) -> dict:
    """Get dashboard overview combining key metrics."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.count(Trace.id).label("total_requests"),
            func.coalesce(func.sum(Trace.cost_usd), 0).label("total_cost"),
            func.coalesce(func.avg(Trace.latency_ms), 0).label("avg_latency"),
            func.coalesce(func.sum(Trace.total_tokens), 0).label("total_tokens"),
            func.sum(case((Trace.status == "error", 1), else_=0)).label("errors"),
            func.sum(case((Trace.cache_hit == True, 1), else_=0)).label("cache_hits"),
        ).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        )
    )
    row = result.one()

    total = int(row.total_requests) if row.total_requests else 0
    errors = int(row.errors) if row.errors else 0
    cache_hits = int(row.cache_hits) if row.cache_hits else 0

    # Active models
    model_result = await db.execute(
        select(Trace.model).where(
            Trace.project_id == project_id,
            Trace.created_at >= since,
        ).distinct()
    )
    active_models = [r.model for r in model_result.all()]

    return {
        "total_requests": total,
        "total_cost_usd": round(float(row.total_cost), 4),
        "avg_latency_ms": round(float(row.avg_latency), 2),
        "error_rate": round(errors / total, 4) if total > 0 else 0,
        "cache_hit_rate": round(cache_hits / total, 4) if total > 0 else 0,
        "cost_saved_usd": 0,  # Will be calculated from cache entries
        "total_tokens": int(row.total_tokens),
        "active_models": active_models,
    }
