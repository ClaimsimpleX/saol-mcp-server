from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from mcp.server import FastMCP
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import uvicorn
import asyncio

# Initialize MCP Server (FastMCP)
mcp = FastMCP("saol-mcp-server")

# Import Tools
from src.tools.firebase_ops import init_firebase, read_queue, update_ticket
from src.tools.graph_ops import init_neo4j, cypher_query
from src.tools.drive_ops import upload_file, delete_file
from src.tools.telemetry_ops import log_mission_receipt
from src.middleware.guardian import guardian_middleware
from src.middleware.telemetry import telemetry_middleware

# Register Tools with Middleware (Chain: Telemetry -> Guardian -> Tool)
# Telemetry should wrap Guardian so it captures the Guardian's block as a result?
# Or Guardian wraps Telemetry?
# If Guardian blocks, the tool isn't called. Telemetry should probably still record the attempt?
# If Telemetry wraps Guardian: Telemetry(Guardian(Tool))
#   -> Telemetry starts
#   -> Guardian checks
#   -> Tool runs (or Guardian raises)
#   -> Telemetry ends (records time)
# This seems correct. We want to measure total time including policy check.

def apply_middleware(tool_func):
    return telemetry_middleware(guardian_middleware(tool_func))

mcp.tool()(apply_middleware(init_firebase))
mcp.tool()(apply_middleware(read_queue))
mcp.tool()(apply_middleware(update_ticket))
mcp.tool()(apply_middleware(init_neo4j))
mcp.tool()(apply_middleware(cypher_query))
mcp.tool()(apply_middleware(upload_file))
mcp.tool()(apply_middleware(delete_file))
mcp.tool()(apply_middleware(log_mission_receipt))

# Define Health Check Tool
@mcp.tool()
async def health_check() -> str:
    """Performs a health check and returns a green dot status."""
    return "Green Dot: Online. Nervous System Interface is active."

# Create a parent FastAPI app to handle routing
app = FastAPI()

# Add Health Check Route
@app.get("/status")
async def handle_status():
    return {"status": "online", "message": "Green Dot: Online"}

# Mount the MCP SSE app
# mcp.sse_app() returns an app that serves /sse and /messages
# Mounting it at /sse means the full path will be /sse/sse
app.mount("/sse", mcp.sse_app())

if __name__ == "__main__":
    print("SAOL MCP Server Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
