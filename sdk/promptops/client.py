"""PromptOps SDK client — wraps LLM providers and auto-logs traces."""

import time
import uuid
import httpx
from typing import Optional, Any
from functools import wraps


class PromptOps:
    """
    PromptOps tracing client.

    Wraps LLM provider clients (OpenAI, Anthropic) and automatically
    sends traces to the PromptOps backend for monitoring and analytics.
    """

    def __init__(
        self,
        api_key: str,
        endpoint: str = "http://localhost:8000",
        environment: str = "production",
        auto_flush: bool = True,
    ):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.environment = environment
        self.auto_flush = auto_flush
        self._buffer = []
        self._http = httpx.Client(
            base_url=self.endpoint,
            headers={"X-API-Key": self.api_key},
            timeout=10.0,
        )

    def _send_trace(self, trace_data: dict):
        """Send a trace to the PromptOps backend."""
        try:
            response = self._http.post("/v1/traces", json=trace_data)
            response.raise_for_status()
        except Exception as e:
            # Never let tracing break the application
            print(f"[PromptOps] Warning: Failed to send trace: {e}")

    def _send_trace_async(self, trace_data: dict):
        """Buffer a trace for batch sending."""
        self._buffer.append(trace_data)
        if self.auto_flush and len(self._buffer) >= 10:
            self.flush()

    def flush(self):
        """Send all buffered traces."""
        if not self._buffer:
            return
        try:
            response = self._http.post(
                "/v1/traces/batch",
                json={"traces": self._buffer},
            )
            response.raise_for_status()
            self._buffer.clear()
        except Exception as e:
            print(f"[PromptOps] Warning: Failed to flush traces: {e}")

    def wrap_openai(self, client: Any) -> Any:
        """
        Wrap an OpenAI client to auto-trace all chat completions.

        Usage:
            from openai import OpenAI
            client = sq.wrap_openai(OpenAI())
        """
        original_create = client.chat.completions.create
        sq = self

        @wraps(original_create)
        def traced_create(*args, **kwargs):
            trace_id = f"trace-{uuid.uuid4().hex[:12]}"
            start_time = time.time()

            try:
                response = original_create(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000

                # Extract data from response
                model = getattr(response, "model", kwargs.get("model", "unknown"))
                usage = getattr(response, "usage", None)

                # Get completion text
                completion = ""
                if hasattr(response, "choices") and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, "message") and hasattr(choice.message, "content"):
                        completion = choice.message.content or ""

                # Build messages from kwargs
                messages = kwargs.get("messages", [])
                prompt = messages[-1].get("content", "") if messages else ""

                trace_data = {
                    "trace_id": trace_id,
                    "model": model,
                    "provider": "openai",
                    "prompt": prompt,
                    "messages": messages,
                    "completion": completion,
                    "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
                    "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
                    "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
                    "latency_ms": round(elapsed_ms, 2),
                    "status": "success",
                    "environment": sq.environment,
                    "metadata": kwargs.get("metadata", {}),
                }
                sq._send_trace(trace_data)
                return response

            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                trace_data = {
                    "trace_id": trace_id,
                    "model": kwargs.get("model", "unknown"),
                    "provider": "openai",
                    "prompt": kwargs.get("messages", [{}])[-1].get("content", "") if kwargs.get("messages") else "",
                    "latency_ms": round(elapsed_ms, 2),
                    "status": "error",
                    "error_message": str(e),
                    "environment": sq.environment,
                }
                sq._send_trace(trace_data)
                raise

        client.chat.completions.create = traced_create
        return client

    def trace(self, name: Optional[str] = None, metadata: Optional[dict] = None):
        """
        Decorator to trace any function call.

        Usage:
            @sq.trace(name="my_function")
            def process_data(input_text):
                ...
        """
        sq = self

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                trace_id = f"trace-{uuid.uuid4().hex[:12]}"
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    elapsed_ms = (time.time() - start_time) * 1000

                    trace_data = {
                        "trace_id": trace_id,
                        "model": "custom",
                        "provider": "custom",
                        "prompt": str(args[0]) if args else "",
                        "completion": str(result)[:1000] if result else "",
                        "latency_ms": round(elapsed_ms, 2),
                        "status": "success",
                        "environment": sq.environment,
                        "metadata": {**(metadata or {}), "function": name or func.__name__},
                    }
                    sq._send_trace(trace_data)
                    return result

                except Exception as e:
                    elapsed_ms = (time.time() - start_time) * 1000
                    trace_data = {
                        "trace_id": trace_id,
                        "model": "custom",
                        "provider": "custom",
                        "latency_ms": round(elapsed_ms, 2),
                        "status": "error",
                        "error_message": str(e),
                        "environment": sq.environment,
                        "metadata": {**(metadata or {}), "function": name or func.__name__},
                    }
                    sq._send_trace(trace_data)
                    raise

            return wrapper
        return decorator

    def __del__(self):
        """Flush remaining traces on cleanup."""
        self.flush()
        self._http.close()
