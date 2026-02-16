"""Cost calculator service — compute USD cost from token usage and model."""

from backend.config import settings


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculate the cost in USD for an LLM call.

    Uses the pricing table from settings. Falls back to GPT-3.5-turbo pricing
    for unknown models.
    """
    # Normalize model name (strip version suffixes for matching)
    model_lower = model.lower().strip()

    # Try exact match first
    pricing = settings.MODEL_PRICING.get(model_lower)

    # Try prefix matching (e.g., "gpt-4-0613" → "gpt-4")
    if pricing is None:
        for key in settings.MODEL_PRICING:
            if model_lower.startswith(key):
                pricing = settings.MODEL_PRICING[key]
                break

    # Default to GPT-3.5-turbo pricing for unknown models
    if pricing is None:
        pricing = settings.MODEL_PRICING.get("gpt-3.5-turbo", {"input": 0.0005, "output": 0.0015})

    input_cost = (prompt_tokens / 1000) * pricing["input"]
    output_cost = (completion_tokens / 1000) * pricing["output"]

    return round(input_cost + output_cost, 6)


def estimate_monthly_savings(
    total_requests: int,
    avg_cost_per_request: float,
    cache_hit_rate: float,
    model_redirect_rate: float = 0.0,
    model_redirect_savings: float = 0.6,  # 60% cheaper on average
) -> dict:
    """
    Estimate monthly savings from caching and model routing.

    Returns a breakdown of savings sources.
    """
    monthly_cost = total_requests * avg_cost_per_request

    cache_savings = monthly_cost * cache_hit_rate
    redirect_savings = (monthly_cost - cache_savings) * model_redirect_rate * model_redirect_savings

    total_savings = cache_savings + redirect_savings
    optimized_cost = monthly_cost - total_savings

    return {
        "current_monthly_cost_usd": round(monthly_cost, 2),
        "cache_savings_usd": round(cache_savings, 2),
        "model_redirect_savings_usd": round(redirect_savings, 2),
        "total_savings_usd": round(total_savings, 2),
        "optimized_cost_usd": round(optimized_cost, 2),
        "savings_percentage": round((total_savings / monthly_cost * 100) if monthly_cost > 0 else 0, 1),
    }
