---
name: ai.agent.integration
description: "Integrate OpenAI Agents SDK to process natural language messages and invoke MCP tools for task management operations. Use when implementing the chat endpoint in FastAPI, processing user messages with AI agent, coordinating between conversation state and tool execution, or debugging agent behavior and tool selection."
category: AI Agent
complexity: High
phase: 3
dependencies: ["OpenAI Agents SDK", "MCP Server", "FastAPI"]
---

# Skill: OpenAI Agents SDK Integration

**Category**: AI Agent
**Complexity**: High
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: OpenAI Agents SDK, MCP Server

## Purpose

Integrate OpenAI Agents SDK to process natural language messages and invoke MCP tools for task management operations.

## When to Use

- Implementing the chat endpoint in FastAPI
- Processing user messages with AI agent
- Coordinating between conversation state and tool execution
- Debugging agent behavior and tool selection

## Pattern

### 1. Agent Configuration

```python
# backend/app/services/agent_service.py
from openai import OpenAI
from openai.agents import Agent, AgentRunner
from typing import List, Dict, Any
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define agent with system instructions
SYSTEM_PROMPT = """You are a helpful AI assistant for managing todo tasks.

You can help users:
- Add new tasks ("Add a task to buy groceries")
- View their tasks ("Show me all my tasks", "What's pending?")
- Complete tasks ("Mark task 3 as done")
- Delete tasks ("Remove the meeting task")
- Update tasks ("Change task 1 to 'Call mom tonight'")

When users mention adding or creating something, use add_task.
When users ask to see or list tasks, use list_tasks.
When users say "done", "complete", or "finished", use complete_task.
When users say "delete", "remove", or "cancel", use delete_task.
When users say "change", "update", or "rename", use update_task.

Always confirm actions with a friendly response.
If a task description is ambiguous, ask for clarification.
Be concise but helpful.
"""

def create_agent() -> Agent:
    """Create an AI agent with MCP tool capabilities."""
    agent = client.agents.create(
        name="todo-assistant",
        model="gpt-4o",
        instructions=SYSTEM_PROMPT,
        tools=[
            {
                "type": "mcp",
                "mcp": {
                    "server_name": "todo-mcp-server",
                    "command": ["python", "-m", "mcp_server.server"]
                }
            }
        ]
    )
    return agent

async def process_message(
    agent: Agent,
    message: str,
    conversation_history: List[Dict[str, str]],
    user_id: str
) -> tuple[str, List[Dict[str, Any]]]:
    """
    Process user message with AI agent.

    Args:
        agent: OpenAI Agent instance
        message: User's message
        conversation_history: Previous messages
        user_id: Current user's ID

    Returns:
        Tuple of (assistant_response, tool_calls)
    """
    # Build message array with history
    messages = conversation_history + [
        {"role": "user", "content": message}
    ]

    # Run agent with context injection (add user_id to all tool calls)
    runner = AgentRunner(agent=agent)

    # Inject user_id into tool calls
    def inject_user_context(tool_name: str, args: dict) -> dict:
        """Add user_id to all tool invocations."""
        return {**args, "user_id": user_id}

    runner.before_tool_call = inject_user_context

    # Execute agent
    result = await runner.run(messages=messages)

    # Extract response and tool calls
    assistant_message = result.messages[-1].content
    tool_calls = [
        {
            "tool": call.function.name,
            "arguments": call.function.arguments,
            "result": call.result
        }
        for call in result.tool_calls
    ]

    return assistant_message, tool_calls
```

### 2. Chat Endpoint Implementation

```python
# backend/app/routes/chat.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.agent_service import create_agent, process_message
from app.services.conversation_service import (
    get_or_create_conversation,
    save_message,
    get_conversation_history
)
from app.dependencies import get_current_user
from typing import Optional, List, Dict, Any

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[Dict[str, Any]]

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Stateless chat endpoint.

    1. Fetch conversation history from database
    2. Process message with AI agent
    3. Store messages in database
    4. Return response
    """
    # Verify user authorization
    if current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Get or create conversation
    conversation = get_or_create_conversation(
        user_id=user_id,
        conversation_id=request.conversation_id
    )

    # Fetch conversation history
    history = get_conversation_history(conversation.id)

    # Store user message
    save_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )

    # Process with AI agent
    agent = create_agent()
    assistant_response, tool_calls = await process_message(
        agent=agent,
        message=request.message,
        conversation_history=history,
        user_id=user_id
    )

    # Store assistant response
    save_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=assistant_response
    )

    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        tool_calls=tool_calls
    )
```

### 3. Error Handling

```python
# backend/app/services/agent_service.py (continued)

class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ToolExecutionError(AgentError):
    """Tool execution failed."""
    pass

class InvalidMessageError(AgentError):
    """Message validation failed."""
    pass

async def safe_process_message(
    agent: Agent,
    message: str,
    conversation_history: List[Dict[str, str]],
    user_id: str
) -> tuple[str, List[Dict[str, Any]]]:
    """Process message with error handling."""

    # Validate message
    if not message or len(message) > 2000:
        raise InvalidMessageError("Message must be 1-2000 characters")

    try:
        return await process_message(
            agent, message, conversation_history, user_id
        )
    except Exception as e:
        # Log error
        print(f"Agent error: {str(e)}")

        # Return fallback response
        fallback_response = (
            "I'm having trouble processing your request right now. "
            "Please try rephrasing or try again later."
        )
        return fallback_response, []
```

## Acceptance Criteria

- [ ] Agent correctly interprets natural language commands
- [ ] user_id is injected into all MCP tool calls
- [ ] Conversation history is included in agent context
- [ ] Tool execution results are captured and returned
- [ ] Error handling gracefully handles agent failures
- [ ] Response latency is under 5 seconds for typical requests
- [ ] Agent behavior matches system prompt instructions

## Testing

```python
# test_agent.py
import pytest
from app.services.agent_service import process_message, create_agent

@pytest.mark.asyncio
async def test_agent_add_task():
    agent = create_agent()
    response, tools = await process_message(
        agent=agent,
        message="Add a task to buy groceries",
        conversation_history=[],
        user_id="test-user"
    )

    assert len(tools) == 1
    assert tools[0]["tool"] == "add_task"
    assert "groceries" in tools[0]["arguments"]["title"].lower()
    assert "added" in response.lower() or "created" in response.lower()

@pytest.mark.asyncio
async def test_agent_list_tasks():
    agent = create_agent()
    response, tools = await process_message(
        agent=agent,
        message="What are my pending tasks?",
        conversation_history=[],
        user_id="test-user"
    )

    assert len(tools) == 1
    assert tools[0]["tool"] == "list_tasks"
    assert tools[0]["arguments"]["status"] == "pending"
```

## Common Issues

1. **Agent doesn't invoke tools**: Check system prompt clarity
2. **Wrong tool selected**: Refine tool descriptions in MCP server
3. **user_id not injected**: Verify `inject_user_context` hook
4. **Conversation context lost**: Ensure history is passed correctly
5. **Rate limiting**: Implement request throttling

## Performance Optimization

- Cache agent instances (reuse across requests)
- Limit conversation history to last 20 messages
- Use streaming responses for better UX
- Implement timeout on agent execution (30s max)

## References

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/guides/agents)
- Phase 3 Spec: `specs/phase3/ai-chatbot.md`
- Related Skills: `mcp.server.setup.md`, `conversation.persistence.md`

## Version

1.0.0 - Initial Phase 3 implementation
