import sys
import os
import asyncio

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.middleware.guardian import guardian_middleware, GuardianBlockError

# Mock Tools
async def mock_upload_file(content: str, filename: str, folder_id: str = None, **kwargs) -> str:
    print(f"[MOCK] Uploading {filename}...")
    return "https://docs.google.com/mock_file_id"

async def mock_delete_file(file_id: str, **kwargs) -> str:
    print(f"[MOCK] Deleting {file_id}...")
    return "Success"

async def mock_cypher_query(query: str, params: dict = {}, **kwargs) -> list:
    print(f"[MOCK] Executing Cypher: {query[:50]}...")
    return [{"a": {"url": params.get("url")}}]

# Wrap with Guardian
protected_upload = guardian_middleware(mock_upload_file)
protected_delete = guardian_middleware(mock_delete_file)
protected_cypher = guardian_middleware(mock_cypher_query)

async def test_asset_trinity():
    print("--- STARTING ASSET TRINITY VERIFICATION ---")

    # 1. Test Drive Upload (Allowed)
    print("\n[TEST 1] Drive Upload (Allowed)")
    try:
        url = await protected_upload(content="test", filename="test.txt", name="upload_file")
        print(f"[SUCCESS] Upload allowed. URL: {url}")
    except GuardianBlockError as e:
        print(f"[FAIL] Upload blocked: {e}")

    # 2. Test Drive Delete (Blocked)
    print("\n[TEST 2] Drive Delete (Blocked)")
    try:
        await protected_delete(file_id="123", name="delete_file")
        print("[FAIL] Delete was NOT blocked!")
    except GuardianBlockError as e:
        print(f"[SUCCESS] Delete blocked as expected: {e}")

    # 3. Test Cypher Link (Allowed)
    print("\n[TEST 3] Codex Link (Allowed)")
    try:
        query = "CREATE (a:Asset {url: $url}) MATCH (t:Ticket) MERGE (t)-[:GENERATED]->(a)"
        result = await protected_cypher(query=query, params={"url": "http://mock"}, name="cypher_query")
        print(f"[SUCCESS] Link allowed. Result: {result}")
    except GuardianBlockError as e:
        print(f"[FAIL] Link blocked: {e}")

    print("\n--- ASSET TRINITY VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_asset_trinity())
