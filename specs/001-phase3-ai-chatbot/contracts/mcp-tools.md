# MCP Tools Contract: AI-Powered Todo Chatbot

**Feature**: 001-phase3-ai-chatbot
**Date**: 2026-01-16
**Purpose**: Define stateless tool contracts for OpenAI Agents SDK integration

## Overview

MCP (Model Context Protocol) tools are stateless functions that the AI agent can invoke to perform database operations. Each tool receives user_id and database session from the FastAPI caller, ensuring user isolation and stateless execution.

## Tool Implementation Pattern

All tools follow this pattern:

```python
from agents import function_tool
from sqlmodel import Session
from typing import Optional, List

@function_tool
def tool_name(
    # Required parameters
    param1: str,
    # Optional parameters
    param2: Optional[str] = None,
    # Injected by FastAPI (not visible to agent)
    session: Session = None,
    user_id: int = None
) -> ReturnType:
    """Tool description for agent context.

    Args:
        param1: Description for agent
        param2: Description for agent

    Returns:
        Description of return value
    """
    # Implementation with user_id filtering
    pass
```

**Key Principles**:
- Tools MUST filter all queries by `user_id`
- Tools MUST NOT store state between calls
- Tools MUST validate inputs (Pydantic handles type validation)
- Tools MUST handle errors gracefully (raise HTTPException for API errors)
- Tools MUST commit transactions explicitly

---

## Tool Definitions

### 1. add_task

**Purpose**: Create a new todo task in the database

**Signature**:
```python
@function_tool
def add_task(
    title: str,
    desc: str = "",
    priority: str = "medium",
    tags: List[str] = [],
    due_date: Optional[str] = None,
    recurring: Optional[str] = None,
    session: Session = None,
    user_id: int = None
) -> int:
    """Add a new todo task to the user's task list.

    Args:
        title: Task title (required, max 255 chars)
        desc: Task description (optional)
        priority: Priority level - must be 'low', 'medium', or 'high' (default: 'medium')
        tags: List of tags for organization (max 10 tags)
        due_date: Due date in ISO format 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SS' (optional)
        recurring: Recurrence pattern - 'daily', 'weekly', 'monthly', or 'yearly' (optional)

    Returns:
        Task ID of newly created task (integer)

    Raises:
        ValueError: If priority not in ['low', 'medium', 'high']
        ValueError: If due_date format invalid
        ValueError: If recurring pattern invalid
    """
    # Validate priority
    if priority not in ["low", "medium", "high"]:
        raise ValueError(f"Invalid priority '{priority}'. Must be low, medium, or high.")

    # Validate and parse due_date
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date)
        except ValueError:
            raise ValueError(f"Invalid due_date format '{due_date}'. Use ISO format (YYYY-MM-DD).")

    # Validate recurring
    if recurring and recurring not in ["daily", "weekly", "monthly", "yearly"]:
        raise ValueError(f"Invalid recurring pattern '{recurring}'.")

    # Create task with user_id filtering
    task = Task(
        user_id=user_id,
        title=title,
        description=desc,
        priority=priority,
        tags=tags,
        due_date=parsed_due_date,
        recurring=recurring
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task.id
```

**Examples**:
```
Agent Call: add_task(title="Buy groceries", priority="high", due_date="2026-01-17")
Response: 123

Agent Call: add_task(title="Review emails", desc="Daily standup prep", recurring="daily")
Response: 124
```

---

### 2. delete_task

**Purpose**: Delete a task by ID with user isolation

**Signature**:
```python
@function_tool
def delete_task(
    task_id: int,
    session: Session = None,
    user_id: int = None
) -> bool:
    """Delete a task from the user's task list.

    IMPORTANT: Agent should confirm with user before calling this tool for destructive actions.

    Args:
        task_id: ID of task to delete (required)

    Returns:
        True if task was deleted successfully, False if task not found

    Raises:
        ValueError: If task_id belongs to different user (security violation)
    """
    # Find task with user_id filtering
    task = session.get(Task, task_id)

    if not task:
        return False  # Task not found

    # Verify ownership
    if task.user_id != user_id:
        raise ValueError(f"Task {task_id} does not belong to user {user_id}")

    # Delete task
    session.delete(task)
    session.commit()
    return True
```

**Examples**:
```
Agent Call: delete_task(task_id=123)
Response: True

Agent Call: delete_task(task_id=999)
Response: False  # Task not found
```

**Agent Prompt Guidance**:
```
When user requests deletion, ALWAYS confirm first:
User: "Delete task 123"
Agent: "Are you sure you want to delete task 'Buy groceries'? This cannot be undone. (yes/no)"
User: "yes"
Agent: <calls delete_task(task_id=123)>
```

---

### 3. update_task

**Purpose**: Update existing task fields

**Signature**:
```python
@function_tool
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    status: Optional[bool] = None,
    recurring: Optional[str] = None,
    session: Session = None,
    user_id: int = None
) -> dict:
    """Update one or more fields of an existing task.

    Only provided fields will be updated. Omitted fields remain unchanged.

    Args:
        task_id: ID of task to update (required)
        title: New task title (optional)
        description: New description (optional)
        priority: New priority - 'low', 'medium', or 'high' (optional)
        tags: New list of tags (replaces existing tags) (optional)
        due_date: New due date in ISO format (optional, use 'null' to clear)
        status: New completion status - true (complete) or false (incomplete) (optional)
        recurring: New recurrence pattern (optional, use 'null' to clear)

    Returns:
        Updated task object as dictionary

    Raises:
        ValueError: If task_id not found or belongs to different user
        ValueError: If validation fails for any field
    """
    # Find task with user_id filtering
    task = session.get(Task, task_id)

    if not task:
        raise ValueError(f"Task {task_id} not found")

    if task.user_id != user_id:
        raise ValueError(f"Task {task_id} does not belong to user {user_id}")

    # Update provided fields with validation
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if priority is not None:
        if priority not in ["low", "medium", "high"]:
            raise ValueError(f"Invalid priority '{priority}'")
        task.priority = priority

    if tags is not None:
        task.tags = tags

    if due_date is not None:
        if due_date == "null":
            task.due_date = None
        else:
            task.due_date = datetime.fromisoformat(due_date)

    if status is not None:
        task.status = status

    if recurring is not None:
        if recurring == "null":
            task.recurring = None
        elif recurring not in ["daily", "weekly", "monthly", "yearly"]:
            raise ValueError(f"Invalid recurring pattern '{recurring}'")
        else:
            task.recurring = recurring

    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)

    return task.dict()
```

**Examples**:
```
Agent Call: update_task(task_id=123, priority="high", due_date="2026-01-18")
Response: {"id": 123, "title": "Buy groceries", "priority": "high", "due_date": "2026-01-18T00:00:00Z", ...}

Agent Call: update_task(task_id=123, status=True)
Response: {"id": 123, "status": True, ...}
```

---

### 4. list_tasks

**Purpose**: Retrieve tasks with optional filtering

**Signature**:
```python
@function_tool
def list_tasks(
    status: Optional[bool] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None,
    limit: int = 50,
    session: Session = None,
    user_id: int = None
) -> List[dict]:
    """List tasks with optional filters.

    Args:
        status: Filter by completion status - true (complete) or false (incomplete) (optional)
        priority: Filter by priority - 'low', 'medium', or 'high' (optional)
        tags: Filter by tags - returns tasks matching ANY tag in list (optional)
        due_before: Filter tasks due before this date (ISO format) (optional)
        due_after: Filter tasks due after this date (ISO format) (optional)
        limit: Maximum number of tasks to return (default: 50, max: 100)

    Returns:
        List of task dictionaries matching filters, ordered by created_at descending
    """
    from sqlmodel import select, or_

    # Build query with user_id filtering
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if status is not None:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        # Match tasks with ANY tag in the list
        tag_conditions = [Task.tags.contains(tag) for tag in tags]
        query = query.where(or_(*tag_conditions))

    if due_before:
        query = query.where(Task.due_date < datetime.fromisoformat(due_before))

    if due_after:
        query = query.where(Task.due_date > datetime.fromisoformat(due_after))

    # Apply limit
    query = query.order_by(Task.created_at.desc()).limit(min(limit, 100))

    # Execute query
    tasks = session.exec(query).all()
    return [task.dict() for task in tasks]
```

**Examples**:
```
Agent Call: list_tasks(status=False, priority="high")
Response: [{"id": 123, "title": "Buy groceries", ...}, {"id": 125, "title": "Submit report", ...}]

Agent Call: list_tasks(due_before="2026-01-17", status=False)
Response: [{"id": 124, "title": "Pay bills", ...}]
```

---

### 5. complete_task

**Purpose**: Toggle task completion status

**Signature**:
```python
@function_tool
def complete_task(
    task_id: int,
    session: Session = None,
    user_id: int = None
) -> bool:
    """Mark a task as complete or toggle completion status.

    Args:
        task_id: ID of task to complete (required)

    Returns:
        New completion status (true if now complete, false if now incomplete)

    Raises:
        ValueError: If task_id not found or belongs to different user
    """
    # Find task with user_id filtering
    task = session.get(Task, task_id)

    if not task:
        raise ValueError(f"Task {task_id} not found")

    if task.user_id != user_id:
        raise ValueError(f"Task {task_id} does not belong to user {user_id}")

    # Toggle status
    task.status = not task.status
    task.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(task)

    return task.status
```

**Examples**:
```
Agent Call: complete_task(task_id=123)
Response: True  # Task is now complete

Agent Call: complete_task(task_id=123)
Response: False  # Task is now incomplete (toggled)
```

---

### 6. search_tasks

**Purpose**: Full-text keyword search across title and description

**Signature**:
```python
@function_tool
def search_tasks(
    query: str,
    limit: int = 20,
    session: Session = None,
    user_id: int = None
) -> List[dict]:
    """Search tasks by keyword in title or description.

    Args:
        query: Search keyword or phrase (required, min 1 char)
        limit: Maximum number of results (default: 20, max: 50)

    Returns:
        List of matching task dictionaries, ordered by relevance (created_at desc)
    """
    from sqlmodel import select, or_

    if not query or len(query) < 1:
        raise ValueError("Query must be at least 1 character")

    # Build case-insensitive search query
    search_pattern = f"%{query}%"
    query_obj = (
        select(Task)
        .where(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
        .order_by(Task.created_at.desc())
        .limit(min(limit, 50))
    )

    tasks = session.exec(query_obj).all()
    return [task.dict() for task in tasks]
```

**Examples**:
```
Agent Call: search_tasks(query="grocery")
Response: [{"id": 123, "title": "Buy groceries", ...}, {"id": 126, "title": "Grocery list review", ...}]

Agent Call: search_tasks(query="meeting")
Response: [{"id": 127, "title": "Team meeting", ...}]
```

---

## Tool Registration with Agent

```python
from agents import Agent, Runner, RunConfig
from agents.run import OpenAIChatCompletionsModel, AsyncOpenAI
import os

# Cohere client
cohere_client = AsyncOpenAI(
    api_key=os.environ["COHERE_API_KEY"],
    base_url="https://api.cohere.ai/v1"
)

# Model config
model = OpenAIChatCompletionsModel(
    model="command-r",
    openai_client=cohere_client
)

# Agent with all tools registered
agent = Agent(
    name="TodoAgent",
    instructions="""You are a helpful Todo assistant. Parse natural language queries and call the appropriate tools.

IMPORTANT RULES:
1. ALWAYS confirm destructive actions (delete, bulk updates) before calling tools
2. For ambiguous queries, ask clarifying questions
3. Filter by user_id is automatic - never ask user for their ID
4. Return only tool results in natural language, no raw JSON
5. If tool raises ValueError, explain error to user in friendly terms

EXAMPLES:
User: "Add task to buy groceries tomorrow"
You: <call add_task(title="Buy groceries", due_date="2026-01-17")>
You: "I've added 'Buy groceries' to your tasks, due tomorrow."

User: "Delete task 123"
You: "Are you sure you want to delete task 'Buy groceries'? (yes/no)"
User: "yes"
You: <call delete_task(task_id=123)>
You: "Task deleted successfully."

User: "Show my high priority tasks"
You: <call list_tasks(priority="high", status=False)>
You: "You have 3 high priority tasks: [list details]"
""",
    tools=[add_task, delete_task, update_task, list_tasks, complete_task, search_tasks]
)

# Run config
run_config = RunConfig(
    model=model,
    model_provider=cohere_client
)

# FastAPI endpoint usage
def process_chat(query: str, user_id: int, db_session: Session) -> str:
    """Process chat query with agent and MCP tools."""

    # Inject user_id and session into tool context
    for tool in agent.tools:
        tool.session = db_session
        tool.user_id = user_id

    # Run agent
    result = Runner.run_sync(agent, query, run_config=run_config)
    return result.final_output
```

---

## Testing MCP Tools

### Unit Tests (pytest)

```python
import pytest
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_add_task(session):
    task_id = add_task(
        title="Test task",
        priority="high",
        session=session,
        user_id=1
    )
    assert task_id > 0

    task = session.get(Task, task_id)
    assert task.title == "Test task"
    assert task.priority == "high"
    assert task.user_id == 1

def test_delete_task_user_isolation(session):
    # Create task for user 1
    task_id = add_task(title="User 1 task", session=session, user_id=1)

    # Try to delete as user 2 (should fail)
    with pytest.raises(ValueError):
        delete_task(task_id=task_id, session=session, user_id=2)

    # Verify task still exists
    task = session.get(Task, task_id)
    assert task is not None

def test_list_tasks_filtering(session):
    # Create tasks
    add_task(title="High priority", priority="high", session=session, user_id=1)
    add_task(title="Low priority", priority="low", session=session, user_id=1)
    add_task(title="User 2 task", priority="high", session=session, user_id=2)

    # List user 1's high priority tasks
    tasks = list_tasks(priority="high", session=session, user_id=1)
    assert len(tasks) == 1
    assert tasks[0]["title"] == "High priority"
```

---

## Security Considerations

### User Isolation
- All tools MUST filter by `user_id` parameter
- `user_id` injected by FastAPI from verified JWT (never from user input)
- Tools MUST validate task ownership before updates/deletes

### Input Validation
- Pydantic handles type validation automatically
- Tools validate business rules (priority values, date formats)
- Tools raise ValueError for invalid inputs (caught by FastAPI)

### Error Handling
- Tools MUST NOT expose internal errors to agent
- ValueError for user-friendly errors
- HTTPException for API errors (handled by FastAPI middleware)

### Audit Logging (Future)
- Log all tool calls with user_id, tool_name, parameters
- Store in audit_log table for compliance
- Implement rate limiting per user

---

## Conclusion

MCP tools provide stateless, type-safe, secure interfaces for the AI agent to interact with the database. All tools enforce user isolation and follow consistent patterns for error handling and validation.

Next step: Create quickstart.md for setup instructions.
