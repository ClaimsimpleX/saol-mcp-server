from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from mcp.server import FastMCP
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import uvicorn
import asyncio

# Initialize FastAPI
app = FastAPI(title="SAOL MCP Server", version="1.0.0")

# Initialize MCP Server (FastMCP)
mcp = FastMCP("saol-mcp-server")

# Define Health Check Tool
@mcp.tool()
async def health_check() -> str:
    """Performs a health check and returns a green dot status."""
    return "Green Dot: Online. Nervous System Interface is active."

# Initialize SSE Transport
sse = SseServerTransport("/sse")

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

@app.post("/sse")
async def handle_sse_post(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())

if __name__ == "__main__":
    print("SAOL MCP Server Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
