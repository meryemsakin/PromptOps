"""Seed data generator — creates realistic demo data for the dashboard."""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

from backend.database import async_session, init_db
from backend.models.project import Project, APIKey
from backend.models.trace import Trace
from backend.services import calculate_cost
from backend.auth import hash_api_key


# Realistic prompts for different use cases
SAMPLE_PROMPTS = [
    ("Summarize this customer complaint and suggest a resolution.", "customer_support"),
    ("Translate the following document to Turkish.", "translation"),
    ("Extract the key entities from this legal contract.", "extraction"),
    ("Generate a product description for an e-commerce listing.", "content"),
    ("Analyze the sentiment of these customer reviews.", "sentiment"),
    ("Write a technical blog post about microservices.", "content"),
    ("Help me debug this Python function that processes JSON.", "coding"),
    ("Classify this support ticket into the correct category.", "classification"),
    ("Create a SQL query to find top customers by revenue.", "coding"),
    ("Summarize this meeting transcript into action items.", "summarization"),
    ("Explain the differences between REST and GraphQL.", "qa"),
    ("Generate unit tests for this authentication module.", "coding"),
    ("What are the KVKK compliance requirements for data storage?", "compliance"),
    ("Rewrite this email to be more professional.", "writing"),
    ("Parse this invoice and extract line items.", "extraction"),
]

MODELS = [
    ("gpt-4o", "openai", 0.35),
    ("gpt-4o-mini", "openai", 0.30),
    ("gpt-3.5-turbo", "openai", 0.15),
    ("claude-3.5-sonnet", "anthropic", 0.10),
    ("claude-3-haiku", "anthropic", 0.10),
]

ENVIRONMENTS = ["production", "staging", "development"]
STATUSES = [("success", 0.92), ("error", 0.06), ("timeout", 0.02)]

ERROR_MESSAGES = [
    "Rate limit exceeded",
    "Context length exceeded: 128000 tokens",
    "Invalid API key",
    "Service temporarily unavailable",
    "Request timeout after 30s",
    "Content filter triggered",
]


async def seed_demo_data(num_traces: int = 10000, days: int = 30):
    """Generate realistic demo data."""
    await init_db()

    async with async_session() as session:
        # Create demo project
        project = Project(
            name="Demo E-Commerce App",
            description="AI-powered e-commerce platform with customer support, content generation, and analytics.",
        )
        session.add(project)
        await session.flush()
        await session.refresh(project)

        # Create API key
        raw_key = "sq-demo-key-for-testing-only-1234567890"
        api_key = APIKey(
            key_hash=hash_api_key(raw_key),
            key_prefix="sq-demo-key-",
            name="Demo Key",
            project_id=project.id,
        )
        session.add(api_key)

        print(f"✅ Created project: {project.name} (ID: {project.id})")
        print(f"🔑 API Key: {raw_key}")

        # Generate traces spread over the time period
        now = datetime.now(timezone.utc)
        traces_created = 0
        batch_size = 500

        for i in range(num_traces):
            # Random timestamp within the period
            hours_ago = random.uniform(0, days * 24)
            timestamp = now - timedelta(hours=hours_ago)

            # Pick model (weighted)
            model_name, provider, _ = random.choices(
                MODELS, weights=[m[2] for m in MODELS], k=1
            )[0]

            # Pick prompt
            prompt_text, category = random.choice(SAMPLE_PROMPTS)

            # Generate realistic token counts
            prompt_tokens = random.randint(50, 2000)
            completion_tokens = random.randint(20, 1500)
            total_tokens = prompt_tokens + completion_tokens

            # Calculate cost
            cost = calculate_cost(model_name, prompt_tokens, completion_tokens)

            # Status (weighted)
            status = random.choices(
                [s[0] for s in STATUSES],
                weights=[s[1] for s in STATUSES],
                k=1
            )[0]

            # Latency (varies by model and status)
            base_latency = {
                "gpt-4o": 800,
                "gpt-4o-mini": 300,
                "gpt-3.5-turbo": 200,
                "claude-3.5-sonnet": 700,
                "claude-3-haiku": 250,
            }.get(model_name, 500)
            latency = max(50, base_latency + random.gauss(0, base_latency * 0.3))
            if status == "timeout":
                latency = 30000

            # Cache hit (15% of requests)
            cache_hit = random.random() < 0.15 if status == "success" else False

            error_msg = None
            if status == "error":
                error_msg = random.choice(ERROR_MESSAGES)

            trace = Trace(
                project_id=project.id,
                trace_id=f"trace-{uuid.uuid4().hex[:12]}",
                model=model_name,
                provider=provider,
                prompt=prompt_text,
                completion=f"[Generated response for: {category}]" if status == "success" else None,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens if status == "success" else 0,
                total_tokens=total_tokens if status == "success" else prompt_tokens,
                cost_usd=cost if status == "success" else calculate_cost(model_name, prompt_tokens, 0),
                latency_ms=round(latency, 2),
                status=status,
                error_message=error_msg,
                cache_hit=cache_hit,
                metadata={"category": category, "user_id": f"user_{random.randint(1, 50)}"},
                environment=random.choices(ENVIRONMENTS, weights=[0.8, 0.15, 0.05], k=1)[0],
                created_at=timestamp,
            )
            session.add(trace)
            traces_created += 1

            # Batch commit for performance
            if traces_created % batch_size == 0:
                await session.flush()
                print(f"  📊 Generated {traces_created}/{num_traces} traces...")

        await session.commit()
        print(f"\n🎉 Seed complete! Generated {traces_created} traces over {days} days.")

        # Print summary stats
        total_cost = sum(
            calculate_cost(
                random.choice(MODELS)[0],
                random.randint(50, 2000),
                random.randint(20, 1500),
            )
            for _ in range(100)
        ) / 100 * num_traces

        print(f"   Estimated total cost: ${total_cost:.2f}")
        print(f"   Cache hit rate: ~15%")
        print(f"   Error rate: ~6%")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
