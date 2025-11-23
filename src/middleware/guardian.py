import functools
import inspect
from typing import Callable, Any
from src.guardian.policy_engine import PolicyEngine, GuardianBlockError

# Initialize Policy Engine
policy_engine = PolicyEngine()

def guardian_middleware(func: Callable) -> Callable:
    """
    Decorator to intercept tool calls and validate them against the Guardian Policy.
    Handles both synchronous and asynchronous functions.
    """
    def _check_policy(*args, **kwargs):
        tool_name = kwargs.get("name") or func.__name__
        # For FastMCP, arguments might be passed as kwargs matching the function signature
        arguments = kwargs
        
        # Mock user profile
        user_profile = {"role": "USER"}
        
        print(f"[GUARDIAN] Intercepting tool: {tool_name}...")
        try:
            policy_engine.check(tool_name, arguments, user_profile)
            print(f"[GUARDIAN] Verdict: ALLOWED.")
        except GuardianBlockError as e:
            print(f"[GUARDIAN] Security Alert: {e}")
            print(f"[GUARDIAN] Verdict: BLOCKED.")
            raise e

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            _check_policy(*args, **kwargs)
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            _check_policy(*args, **kwargs)
            return func(*args, **kwargs)
        return sync_wrapper
