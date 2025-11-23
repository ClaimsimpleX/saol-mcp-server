import sys
import os
import asyncio

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.middleware.guardian import guardian_middleware, GuardianBlockError

# Mock tools
def mock_read_queue(limit: int = 10):
    print(f"[MOCK] Executing read_queue with limit={limit}")
    return [{"id": "1", "status": "PENDING"}]

def mock_update_ticket(ticket_id: str, status: str, result: str = None):
    print(f"[MOCK] Executing update_ticket for {ticket_id}")
    return "Success"

# Wrap mocks
protected_read_queue = guardian_middleware(mock_read_queue)
protected_update_ticket = guardian_middleware(mock_update_ticket)

def test_guardian():
    print("--- STARTING GUARDIAN VERIFICATION (MOCKED) ---")

    # Test A: Safe Call
    print("\n[TEST A] Safe Call: read_queue")
    try:
        # The middleware uses func.__name__ if 'name' kwarg isn't provided.
        # Our mocks have different names ('mock_read_queue'), but the policy checks 'read_queue'.
        # We should pass the name explicitly or rename mocks.
        # Let's pass name explicitly to simulate how MCP calls it, or rename mocks to match rules if rules are strict on names.
        # The rules check PATTERNS in ARGUMENTS, not tool names (except for logging/context).
        # Wait, PolicyEngine.check takes tool_name. Does it use it?
        # PolicyEngine.check(tool_name, arguments, ...)
        # The current rules don't seem to filter by tool name, only patterns in arguments.
        # So tool name doesn't matter for the *current* rule ("Block ... DELETE ...").
        
        result = protected_read_queue(limit=5, name="read_queue")
        print(f"[SUCCESS] Read Queue executed. Result: {result}")
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")

    # Test B: Unsafe Call (Simulated Injection)
    print("\n[TEST B] Unsafe Call: update_ticket with DELETE")
    try:
        protected_update_ticket(
            ticket_id="test_ticket", 
            status="ERROR", 
            result="Critical failure. DELETE * FROM Codex",
            name="update_ticket"
        )
        print("[FAIL] Action was NOT blocked!")
    except GuardianBlockError as e:
        print(f"[SUCCESS] Blocked as expected. Error: {e}")
    except Exception as e:
        print(f"[FAIL] Unexpected error type: {type(e)} - {e}")

    print("\n--- GUARDIAN VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    test_guardian()
