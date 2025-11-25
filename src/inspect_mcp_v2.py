from mcp.server import FastMCP
print("Imported FastMCP")
mcp = FastMCP("test")
print(f"Type: {type(mcp)}")
print(f"Dir: {dir(mcp)}")
try:
    print(f"SSE App: {mcp.sse_app}")
except Exception as e:
    print(f"Error accessing sse_app: {e}")
