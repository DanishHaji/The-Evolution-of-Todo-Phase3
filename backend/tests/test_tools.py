"""Unit tests for MCP tools (TDD approach)."""

import pytest
from datetime import datetime, timedelta
from app.mcp_tools import (
    add_task,
    delete_task,
    update_task,
    list_tasks,
    complete_task,
    search_tasks
)


def test_add_task_creates_with_user_id(test_session, test_user):
    """Test add_task creates task with correct user_id filtering."""
    task_id = add_task(
        title="Buy groceries",
        desc="Milk, eggs, bread",
        priority="high",
        tags=["shopping", "urgent"],
        session=test_session,
        user_id=test_user.id
    )

    assert task_id > 0

    # Verify task exists in database
    from app.models import Task
    task = test_session.get(Task, task_id)
    assert task is not None
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.priority == "high"
    assert task.tags == ["shopping", "urgent"]
    assert task.user_id == test_user.id
    assert task.status is False


def test_add_task_with_due_date(test_session, test_user):
    """Test add_task parses ISO date correctly."""
    due_date_str = "2026-01-20T15:30:00"
    task_id = add_task(
        title="Meeting",
        due_date=due_date_str,
        session=test_session,
        user_id=test_user.id
    )

    from app.models import Task
    task = test_session.get(Task, task_id)
    assert task.due_date is not None
    assert task.due_date.year == 2026
    assert task.due_date.month == 1
    assert task.due_date.day == 20


def test_add_task_validates_priority(test_session, test_user):
    """Test add_task rejects invalid priority."""
    with pytest.raises(ValueError, match="Invalid priority"):
        add_task(
            title="Test",
            priority="invalid",
            session=test_session,
            user_id=test_user.id
        )


def test_add_task_validates_recurring(test_session, test_user):
    """Test add_task rejects invalid recurring pattern."""
    with pytest.raises(ValueError, match="Invalid recurring pattern"):
        add_task(
            title="Test",
            recurring="hourly",  # Invalid
            session=test_session,
            user_id=test_user.id
        )


def test_add_task_validates_due_date_format(test_session, test_user):
    """Test add_task rejects invalid date format."""
    with pytest.raises(ValueError, match="Invalid due_date format"):
        add_task(
            title="Test",
            due_date="invalid-date",
            session=test_session,
            user_id=test_user.id
        )


def test_add_task_limits_tags(test_session, test_user):
    """Test add_task limits tags to 10."""
    task_id = add_task(
        title="Test",
        tags=[f"tag{i}" for i in range(15)],  # 15 tags
        session=test_session,
        user_id=test_user.id
    )

    from app.models import Task
    task = test_session.get(Task, task_id)
    assert len(task.tags) == 10  # Should limit to 10


def test_delete_task_verifies_ownership(test_session, test_user):
    """Test delete_task raises ValueError if user tries to delete another user's task."""
    # Create task for user 1
    task_id = add_task(
        title="User 1 task",
        session=test_session,
        user_id=test_user.id
    )

    # Try to delete as user 2 (different user)
    with pytest.raises(ValueError, match="does not belong to user"):
        delete_task(task_id=task_id, session=test_session, user_id=999)

    # Verify task still exists
    from app.models import Task
    task = test_session.get(Task, task_id)
    assert task is not None


def test_delete_task_returns_false_if_not_found(test_session, test_user):
    """Test delete_task returns False if task doesn't exist."""
    result = delete_task(
        task_id=99999,
        session=test_session,
        user_id=test_user.id
    )
    assert result is False


def test_delete_task_success(test_session, test_user):
    """Test delete_task successfully deletes task."""
    task_id = add_task(
        title="To be deleted",
        session=test_session,
        user_id=test_user.id
    )

    result = delete_task(
        task_id=task_id,
        session=test_session,
        user_id=test_user.id
    )

    assert result is True

    # Verify task is deleted
    from app.models import Task
    task = test_session.get(Task, task_id)
    assert task is None


def test_update_task_modifies_fields(test_session, test_user):
    """Test update_task modifies specified fields correctly."""
    task_id = add_task(
        title="Original title",
        desc="Original description",
        priority="low",
        session=test_session,
        user_id=test_user.id
    )

    updated_task = update_task(
        task_id=task_id,
        title="Updated title",
        priority="high",
        session=test_session,
        user_id=test_user.id
    )

    assert updated_task["title"] == "Updated title"
    assert updated_task["priority"] == "high"
    assert updated_task["description"] == "Original description"  # Unchanged


def test_update_task_verifies_ownership(test_session, test_user):
    """Test update_task raises ValueError if user tries to update another user's task."""
    task_id = add_task(
        title="User 1 task",
        session=test_session,
        user_id=test_user.id
    )

    with pytest.raises(ValueError, match="does not belong to user"):
        update_task(
            task_id=task_id,
            title="Hacked",
            session=test_session,
            user_id=999
        )


def test_update_task_clears_optional_fields(test_session, test_user):
    """Test update_task can clear optional fields with 'null'."""
    task_id = add_task(
        title="Test",
        due_date="2026-01-20",
        recurring="daily",
        session=test_session,
        user_id=test_user.id
    )

    updated_task = update_task(
        task_id=task_id,
        due_date="null",
        recurring="null",
        session=test_session,
        user_id=test_user.id
    )

    assert updated_task["due_date"] is None
    assert updated_task["recurring"] is None


def test_list_tasks_filters_by_status(test_session, test_user):
    """Test list_tasks filters by completion status."""
    # Create completed and incomplete tasks
    add_task(title="Incomplete 1", session=test_session, user_id=test_user.id)
    task_id = add_task(title="Complete 1", session=test_session, user_id=test_user.id)
    complete_task(task_id=task_id, session=test_session, user_id=test_user.id)
    add_task(title="Incomplete 2", session=test_session, user_id=test_user.id)

    # List only incomplete tasks
    incomplete_tasks = list_tasks(
        status=False,
        session=test_session,
        user_id=test_user.id
    )
    assert len(incomplete_tasks) == 2
    assert all(task["status"] is False for task in incomplete_tasks)

    # List only complete tasks
    complete_tasks = list_tasks(
        status=True,
        session=test_session,
        user_id=test_user.id
    )
    assert len(complete_tasks) == 1
    assert complete_tasks[0]["title"] == "Complete 1"


def test_list_tasks_filters_by_priority(test_session, test_user):
    """Test list_tasks filters by priority."""
    add_task(title="High 1", priority="high", session=test_session, user_id=test_user.id)
    add_task(title="Low 1", priority="low", session=test_session, user_id=test_user.id)
    add_task(title="High 2", priority="high", session=test_session, user_id=test_user.id)

    high_tasks = list_tasks(
        priority="high",
        session=test_session,
        user_id=test_user.id
    )
    assert len(high_tasks) == 2
    assert all(task["priority"] == "high" for task in high_tasks)


def test_list_tasks_filters_by_tags(test_session, test_user):
    """Test list_tasks filters by tags (ANY match)."""
    add_task(title="Task 1", tags=["work", "urgent"], session=test_session, user_id=test_user.id)
    add_task(title="Task 2", tags=["personal"], session=test_session, user_id=test_user.id)
    add_task(title="Task 3", tags=["work"], session=test_session, user_id=test_user.id)

    work_tasks = list_tasks(
        tags=["work"],
        session=test_session,
        user_id=test_user.id
    )
    assert len(work_tasks) == 2


def test_list_tasks_filters_by_user_id(test_session, test_user):
    """Test list_tasks only returns tasks for specific user."""
    from app.models import User

    # Create second user
    user2 = User(email="user2@example.com", password_hash="hash2")
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user2)

    # Create tasks for both users
    add_task(title="User 1 task", session=test_session, user_id=test_user.id)
    add_task(title="User 2 task", session=test_session, user_id=user2.id)

    # List user 1's tasks
    user1_tasks = list_tasks(session=test_session, user_id=test_user.id)
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["title"] == "User 1 task"


def test_complete_task_toggles_status(test_session, test_user):
    """Test complete_task toggles task completion status."""
    task_id = add_task(title="Test", session=test_session, user_id=test_user.id)

    # First toggle: incomplete -> complete
    status1 = complete_task(task_id=task_id, session=test_session, user_id=test_user.id)
    assert status1 is True

    # Second toggle: complete -> incomplete
    status2 = complete_task(task_id=task_id, session=test_session, user_id=test_user.id)
    assert status2 is False


def test_complete_task_verifies_ownership(test_session, test_user):
    """Test complete_task raises ValueError if user tries to complete another user's task."""
    task_id = add_task(title="User 1 task", session=test_session, user_id=test_user.id)

    with pytest.raises(ValueError, match="does not belong to user"):
        complete_task(task_id=task_id, session=test_session, user_id=999)


def test_search_tasks_finds_by_title(test_session, test_user):
    """Test search_tasks finds tasks by keyword in title."""
    add_task(title="Buy groceries", session=test_session, user_id=test_user.id)
    add_task(title="Grocery list review", session=test_session, user_id=test_user.id)
    add_task(title="Team meeting", session=test_session, user_id=test_user.id)

    # Search for "grocer" which appears in both "groceries" and "Grocery"
    results = search_tasks(query="grocer", session=test_session, user_id=test_user.id)
    assert len(results) == 2
    assert all("grocer" in task["title"].lower() for task in results)


def test_search_tasks_finds_by_description(test_session, test_user):
    """Test search_tasks finds tasks by keyword in description."""
    add_task(title="Task 1", desc="Discuss project timeline", session=test_session, user_id=test_user.id)
    add_task(title="Task 2", desc="Review code", session=test_session, user_id=test_user.id)

    results = search_tasks(query="project", session=test_session, user_id=test_user.id)
    assert len(results) == 1
    assert "project" in results[0]["description"].lower()


def test_search_tasks_case_insensitive(test_session, test_user):
    """Test search_tasks is case-insensitive."""
    add_task(title="URGENT Meeting", session=test_session, user_id=test_user.id)

    results = search_tasks(query="urgent", session=test_session, user_id=test_user.id)
    assert len(results) == 1


def test_search_tasks_validates_query(test_session, test_user):
    """Test search_tasks requires non-empty query."""
    with pytest.raises(ValueError, match="Query must be at least 1 character"):
        search_tasks(query="", session=test_session, user_id=test_user.id)


def test_search_tasks_limits_results(test_session, test_user):
    """Test search_tasks respects limit parameter."""
    for i in range(30):
        add_task(title=f"Task {i}", session=test_session, user_id=test_user.id)

    results = search_tasks(query="Task", limit=10, session=test_session, user_id=test_user.id)
    assert len(results) == 10
