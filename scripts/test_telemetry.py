import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add Conductor src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../saol-conductor-gke/src')))

from src.middleware.guardian import guardian_middleware
from src.middleware.telemetry import telemetry_middleware
# Import directly from spokes since we added src to path
from spokes.mcp_worker_spoke import MockMcpWorkerSpoke

# Mock Tools
async def mock_read_queue(limit: int = 10, **kwargs) -> list:
    print(f"[MOCK] Reading queue...")
    return [{"id": "ticket-123"}]

async def mock_update_ticket(ticket_id: str, status: str, result: str = None, **kwargs) -> str:
    print(f"[MOCK] Updating ticket {ticket_id}...")
    return "Success"

async def mock_log_mission_receipt(receipt: Dict[str, Any], **kwargs) -> str:
    print(f"[MOCK] Logging receipt for {receipt.get('ticket_id')} (Status: {receipt.get('status')})")
    # print(f"Receipt: {receipt}")
    return "Telemetry Logged"

# Apply Middleware (Telemetry -> Guardian -> Tool)
# Note: We need to mock Guardian passing too, or just use Telemetry middleware for this test if we trust Guardian works.
# But let's use the full chain if possible.
# Since we don't have a real PolicyEngine loaded with rules for these mocks, Guardian might block if we don't be careful.
# But our mocks are safe.
# However, Guardian expects 'name' kwarg or func name.
# Let's just use Telemetry middleware for this specific test to verify "The Accountant" logic.
# The integration test verified the chain.

wrapped_read_queue = telemetry_middleware(mock_read_queue)
wrapped_update_ticket = telemetry_middleware(mock_update_ticket)
wrapped_log_receipt = telemetry_middleware(mock_log_mission_receipt)

class MockTools:
    def __init__(self):
        self.read_queue = wrapped_read_queue
        self.update_ticket = wrapped_update_ticket
        self.log_mission_receipt = wrapped_log_receipt

async def test_telemetry():
    print("--- STARTING TELEMETRY VERIFICATION ---")
    
    tools = MockTools()
    spoke = MockMcpWorkerSpoke(tools)
    
    # Test 1: Success Case
    print("\n[TEST 1] Success Case")
    ticket = {"id": "ticket-success-001"}
    await spoke.run(ticket)
    
    # Test 2: Failure Case (Crash)
    print("\n[TEST 2] Failure Case (Crash)")
    ticket_fail = {"id": "ticket-fail-002", "simulate_failure": True}
    await spoke.run(ticket_fail)
    
    print("\n--- TELEMETRY VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    # Need to fix import path for saol_conductor_gke since it's in a parallel dir
    # We added '..' to sys.path, so 'saol-conductor-gke' is a folder there.
    # But python module names can't have hyphens.
    # We might need to adjust sys.path to point INSIDE saol-conductor-gke/src?
    # Or just copy the mock class here for simplicity if imports are messy.
    # Let's try to import dynamically or adjust path.
    
    # Actually, let's just define the MockSpoke here if the import fails, 
    # but I already wrote the file.
    # Let's fix the import path.
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../saol-conductor-gke/src')))
    # Now we can import spokes.mcp_worker_spoke
    
    asyncio.run(test_telemetry())
