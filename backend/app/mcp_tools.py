"""MCP Tools for AI-Powered Todo Chatbot.

Stateless functions that the AI agent can invoke to perform database operations.
Each tool enforces user isolation and follows consistent error handling patterns.
"""

from sqlmodel import Session, select, or_
from typing import Optional, List
from datetime import datetime
from app.models import Task


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
        tags=tags[:10],  # Limit to 10 tags
        due_date=parsed_due_date,
        recurring=recurring
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task.id


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
        task.tags = tags[:10]  # Limit to 10 tags

    if due_date is not None:
        if due_date == "null":
            task.due_date = None
        else:
            try:
                task.due_date = datetime.fromisoformat(due_date)
            except ValueError:
                raise ValueError(f"Invalid due_date format '{due_date}'. Use ISO format.")

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

    return task.model_dump()


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
    # Build query with user_id filtering
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if status is not None:
        query = query.where(Task.status == status)

    if priority:
        query = query.where(Task.priority == priority)

    if tags:
        # Match tasks with ANY tag in the list
        # Use string matching which works for both SQLite (testing) and PostgreSQL
        from sqlalchemy import cast
        from sqlalchemy.types import String
        tag_conditions = [
            cast(Task.tags, String).like(f'%"{tag}"%')
            for tag in tags
        ]
        query = query.where(or_(*tag_conditions))

    if due_before:
        try:
            due_before_date = datetime.fromisoformat(due_before)
            query = query.where(Task.due_date < due_before_date)
        except ValueError:
            raise ValueError(f"Invalid due_before format '{due_before}'. Use ISO format.")

    if due_after:
        try:
            due_after_date = datetime.fromisoformat(due_after)
            query = query.where(Task.due_date > due_after_date)
        except ValueError:
            raise ValueError(f"Invalid due_after format '{due_after}'. Use ISO format.")

    # Apply limit
    query = query.order_by(Task.created_at.desc()).limit(min(limit, 100))

    # Execute query
    tasks = session.exec(query).all()
    return [task.model_dump() for task in tasks]


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
    if not query or len(query) < 1:
        raise ValueError("Query must be at least 1 character")

    # Build case-insensitive search query
    # Use lower() for SQLite compatibility (ilike not fully supported in SQLite)
    from sqlalchemy import func
    search_pattern = f"%{query.lower()}%"
    query_obj = (
        select(Task)
        .where(
            Task.user_id == user_id,
            or_(
                func.lower(Task.title).like(search_pattern),
                func.lower(Task.description).like(search_pattern)
            )
        )
        .order_by(Task.created_at.desc())
        .limit(min(limit, 50))
    )

    tasks = session.exec(query_obj).all()
    return [task.model_dump() for task in tasks]
