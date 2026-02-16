"""
PromptOps Python SDK — instrument your LLM calls with zero effort.

Usage:
    from promptops import PromptOps

    sq = PromptOps(api_key="sq-your-key", endpoint="http://localhost:8000")

    # Wrap OpenAI client
    client = sq.wrap_openai(OpenAI())
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    # Trace is automatically logged!
"""

__version__ = "0.1.0"

from promptops.client import PromptOps

__all__ = ["PromptOps"]
