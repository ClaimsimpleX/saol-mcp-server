# SAOL MCP Server: The Nervous System Interface

This repository houses the Model Context Protocol (MCP) server for the SAOL ecosystem. It serves as the persistent bridge between agents and the shared memory systems (Firebase Firestore, Neo4j Codex).

## Features
- **Protocol**: MCP over SSE (Server-Sent Events)
- **Transport**: FastAPI
- **Memory**: Firebase Admin SDK, Neo4j Driver

## Quick Start
```bash
# Install dependencies
pip install .

# Run Server
uvicorn src.main:app --port 8080
```

## Tools
- `health_check`: Verifies system connectivity.
