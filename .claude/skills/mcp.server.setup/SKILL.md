---
name: mcp.server.setup
description: "Set up and configure an MCP (Model Context Protocol) server that exposes todo task operations as tools for AI agents to invoke. Use when implementing the backend MCP server for Phase 3, adding new MCP tools, testing tool integration with OpenAI Agents SDK, or debugging tool invocation issues."
category: MCP Integration
complexity: Medium
phase: 3
dependencies: ["Official MCP SDK", "FastAPI", "SQLModel"]
---

# Skill: MCP Server Setup

**Category**: MCP Integration
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: Official MCP SDK, FastAPI

## Purpose

Set up and configure an MCP (Model Context Protocol) server that exposes todo task operations as tools for AI agents to invoke.

## When to Use

- Implementing the backend MCP server for Phase 3
- Adding new MCP tools for task operations
- Testing MCP tool integration with OpenAI Agents SDK
- Debugging tool invocation issues

## Pattern

### 1. MCP Server Structure

```python
# backend/mcp_server/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from typing import Any
import asyncio

# Initialize MCP server
app = Server("todo-mcp-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="add_task",
            description="Create a new todo task for the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description (optional)"}
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="Retrieve all tasks for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter by task status"
                    }
                },
                "required": ["user_id"]
            }
        ),
        # Add other tools...
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool invocation."""
    if name == "add_task":
        return await add_task_handler(arguments)
    elif name == "list_tasks":
        return await list_tasks_handler(arguments)
    # Handle other tools...

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Tool Handler Implementation

```python
# backend/mcp_server/handlers.py
from sqlmodel import Session, select
from app.models import Task
from app.database import get_session
from mcp.types import TextContent
import json

async def add_task_handler(args: dict) -> list[TextContent]:
    """Handle add_task tool invocation."""
    user_id = args["user_id"]
    title = args["title"]
    description = args.get("description", "")

    # Validate inputs
    if not title or len(title) > 200:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Title must be 1-200 characters",
                "status": "failed"
            })
        )]

    # Create task in database
    with get_session() as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return [TextContent(
            type="text",
            text=json.dumps({
                "task_id": task.id,
                "status": "created",
                "title": task.title
            })
        )]

async def list_tasks_handler(args: dict) -> list[TextContent]:
    """Handle list_tasks tool invocation."""
    user_id = args["user_id"]
    status_filter = args.get("status", "all")

    with get_session() as session:
        query = select(Task).where(Task.user_id == user_id)

        if status_filter == "pending":
            query = query.where(Task.completed == False)
        elif status_filter == "completed":
            query = query.where(Task.completed == True)

        tasks = session.exec(query).all()

        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

        return [TextContent(
            type="text",
            text=json.dumps(task_list)
        )]
```

### 3. Integration with FastAPI

```python
# backend/app/main.py
from fastapi import FastAPI
from app.routes import chat

app = FastAPI(title="Todo Chatbot API")

# Include chat routes
app.include_router(chat.router, prefix="/api")

# MCP server runs separately via stdio
# Start with: python -m mcp_server.server
```

## Acceptance Criteria

- [ ] MCP server exposes all 5 required tools (add, list, complete, delete, update)
- [ ] Tool schemas are valid and include all required parameters
- [ ] Tool handlers interact with database correctly
- [ ] Error handling returns structured error responses
- [ ] Tools are stateless (no server-side state between calls)
- [ ] User isolation is enforced (user_id checked on all operations)

## Testing

```bash
# Test MCP server with MCP Inspector
npx @modelcontextprotocol/inspector python -m mcp_server.server

# Test tool invocation
curl -X POST http://localhost:8000/mcp/call-tool \
  -H "Content-Type: application/json" \
  -d '{"name": "add_task", "arguments": {"user_id": "test", "title": "Buy milk"}}'
```

## Common Issues

1. **Tool not found**: Ensure tool name in `call_tool()` matches `list_tools()`
2. **Schema validation errors**: Check inputSchema matches JSON Schema spec
3. **Database connection issues**: Verify DATABASE_URL in environment
4. **User isolation failure**: Always filter by user_id in queries

## References

- [Official MCP SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- Phase 3 Spec: `specs/phase3/mcp-tools.md`
- Related Skills: `ai.agent.integration.md`, `db.task.operations.md`

## Version

1.0.0 - Initial Phase 3 implementation
