import functools
import inspect
import time
from typing import Callable, Dict
from collections import defaultdict

# Simple in-memory store for the current session's tool usage.
# In a real production server, this would be context-local (ContextVar).
# For this MVP, we'll assume single-threaded or use a global dict keyed by something unique if possible,
# but since we don't have a session ID in the tool call args easily, we'll just use a global counter for now
# and assume the Spoke aggregates its own view or we reset it.
# ACTUALLY: The requirement says "Accumulate stats in a temporary session state".
# Since FastMCP doesn't expose a session object easily in the tool wrapper without context,
# and the Spoke is responsible for sending the FINAL receipt, the Middleware here is acting as a "Meter"
# that might just log to stdout or update a global metric for monitoring.
# BUT, if the Spoke needs to know its own usage from the Server, the Server would need to return it?
# No, the Spoke calls the tools. The Spoke knows what it called.
# The Middleware here is for the SERVER'S observability (The Accountant's view).
# So we will log it and potentially store it in a global "ledger" for the server's lifetime.

# Let's implement a simple global counter for now to demonstrate the interception.

tool_usage_stats: Dict[str, int] = defaultdict(int)

def telemetry_middleware(func: Callable) -> Callable:
    """
    Decorator to track tool execution time and usage count.
    """
    def _record_usage(tool_name: str, duration: float):
        tool_usage_stats[tool_name] += 1
        print(f"[TELEMETRY] Tool '{tool_name}' executed in {duration:.4f}s. Total calls: {tool_usage_stats[tool_name]}")

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tool_name = kwargs.get("name") or func.__name__
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                _record_usage(tool_name, duration)
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tool_name = kwargs.get("name") or func.__name__
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                _record_usage(tool_name, duration)
        return sync_wrapper
