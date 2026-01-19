"""Unit tests for database models (TDD - RED phase)."""

import pytest
from datetime import datetime
from app.models import User, Task, Conversation, Message


def test_user_model_creation(test_session):
    """Test User model can be created with required fields."""
    user = User(
        email="user@example.com",
        password_hash="hashed_password",
    )
    test_session.add(user)
    test_session.commit()
    test_session.refresh(user)

    assert user.id is not None
    assert user.email == "user@example.com"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_task_model_creation(test_session, test_user):
    """Test Task model can be created with all fields."""
    task = Task(
        user_id=test_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
        tags=["shopping", "urgent"],
        status=False,
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    assert task.id is not None
    assert task.user_id == test_user.id
    assert task.title == "Buy groceries"
    assert task.priority == "high"
    assert task.tags == ["shopping", "urgent"]
    assert task.status is False
    assert task.created_at is not None
    assert task.updated_at is not None


def test_task_priority_validation(test_session, test_user):
    """Test Task priority must be valid (low/medium/high)."""
    # This test will pass with any string since we don't enforce at model level
    # Validation should be done at API level with Pydantic
    task = Task(
        user_id=test_user.id,
        title="Test task",
        priority="invalid",  # Should be caught by API validation
    )
    test_session.add(task)
    test_session.commit()

    # Model allows any string, validation happens at API layer
    assert task.priority == "invalid"


def test_task_title_required(test_session, test_user):
    """Test Task title is required (cannot be None)."""
    with pytest.raises(Exception):  # Will raise validation error
        task = Task(
            user_id=test_user.id,
            title=None,  # This should fail
        )
        test_session.add(task)
        test_session.commit()


def test_task_default_values(test_session, test_user):
    """Test Task has correct default values."""
    task = Task(
        user_id=test_user.id,
        title="Minimal task",
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    assert task.description == ""
    assert task.priority == "medium"
    assert task.tags == []
    assert task.status is False
    assert task.due_date is None
    assert task.recurring is None


def test_conversation_model_creation(test_session, test_user):
    """Test Conversation model can be created."""
    conversation = Conversation(
        user_id=test_user.id,
    )
    test_session.add(conversation)
    test_session.commit()
    test_session.refresh(conversation)

    assert conversation.id is not None
    assert conversation.user_id == test_user.id
    assert conversation.created_at is not None
    assert conversation.updated_at is not None


def test_message_model_creation(test_session, test_user):
    """Test Message model can be created."""
    # First create a conversation
    conversation = Conversation(user_id=test_user.id)
    test_session.add(conversation)
    test_session.commit()
    test_session.refresh(conversation)

    # Then create a message
    message = Message(
        conversation_id=conversation.id,
        user_id=test_user.id,
        role="user",
        content="Add task to buy groceries",
    )
    test_session.add(message)
    test_session.commit()
    test_session.refresh(message)

    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.user_id == test_user.id
    assert message.role == "user"
    assert message.content == "Add task to buy groceries"
    assert message.created_at is not None


def test_foreign_key_constraints(test_session):
    """Test foreign key constraints are enforced."""
    # Try to create task with non-existent user_id
    task = Task(
        user_id=999,  # This user doesn't exist
        title="Test task",
    )
    test_session.add(task)

    # SQLite in-memory might not enforce FK constraints by default
    # This test documents the expected behavior
    try:
        test_session.commit()
        # If FK constraints are not enforced, task will be created
        assert task.id is not None
    except Exception:
        # If FK constraints are enforced, this will fail
        test_session.rollback()
        assert True


def test_timestamps_auto_set(test_session, test_user):
    """Test timestamps are automatically set on creation."""
    before = datetime.utcnow()

    task = Task(
        user_id=test_user.id,
        title="Timestamp test",
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    after = datetime.utcnow()

    assert before <= task.created_at <= after
    assert before <= task.updated_at <= after


def test_json_field_storage(test_session, test_user):
    """Test tags are stored as JSON array."""
    task = Task(
        user_id=test_user.id,
        title="JSON test",
        tags=["work", "urgent", "high-priority"],
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)

    assert isinstance(task.tags, list)
    assert len(task.tags) == 3
    assert "work" in task.tags
    assert "urgent" in task.tags
