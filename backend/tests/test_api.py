"""Integration tests for Chat API endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import contextlib

from app.main import app
from app.auth import create_jwt_token
from app.models import get_session


@pytest.fixture
def client(test_session):
    """Create test client with overridden database session."""
    def override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = override_get_session
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_agent_response():
    """Mock agent response."""
    @contextlib.contextmanager
    def _mock(response_text="Task added successfully"):
        with patch('app.chat.run_agent') as mock_run_agent:
            mock_run_agent.return_value = response_text
            yield mock_run_agent
    return _mock


def test_chat_endpoint_with_valid_jwt_and_query(client, test_user, test_session, mock_agent_response):
    """Test POST /api/{user_id}/chat with valid JWT and query."""
    # Create JWT token for test user
    token = create_jwt_token(test_user.id)

    # Mock agent response
    with mock_agent_response("Done! I've added 'Buy groceries' to your tasks."):
        # Make request
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"query": "Add task to buy groceries"},
            headers={"Authorization": f"Bearer {token}"}
        )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert data["conversation_id"] > 0


def test_chat_endpoint_returns_401_with_invalid_jwt(client, test_user):
    """Test POST /api/{user_id}/chat returns 401 with invalid JWT."""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"query": "Add task"},
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]


def test_chat_endpoint_returns_401_with_missing_jwt(client, test_user):
    """Test POST /api/{user_id}/chat returns 401 with missing JWT."""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"query": "Add task"}
        # No Authorization header
    )

    assert response.status_code == 401


def test_chat_endpoint_returns_403_with_user_id_mismatch(client, test_session, mock_agent_response):
    """Test POST /api/{user_id}/chat returns 403 when path user_id doesn't match JWT."""
    from app.models import User

    # Create two users
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    # Create JWT token for user1
    token = create_jwt_token(user1.id)

    with mock_agent_response():
        # Try to access user2's endpoint with user1's token
        response = client.post(
            f"/api/{user2.id}/chat",
            json={"query": "Add task"},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
    assert "User ID mismatch" in response.json()["detail"]


def test_chat_endpoint_returns_400_with_empty_query(client, test_user):
    """Test POST /api/{user_id}/chat returns 400 with empty query."""
    token = create_jwt_token(test_user.id)

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"query": ""},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_chat_endpoint_returns_400_with_whitespace_query(client, test_user):
    """Test POST /api/{user_id}/chat returns 400 with whitespace-only query."""
    token = create_jwt_token(test_user.id)

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"query": "   "},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


def test_chat_endpoint_creates_new_conversation(client, test_user, test_session, mock_agent_response):
    """Test chat endpoint creates new conversation when conversation_id not provided."""
    token = create_jwt_token(test_user.id)

    with mock_agent_response("Response"):
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"query": "Add task"},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]

    # Verify conversation was created in database
    from app.models import Conversation
    conversation = test_session.get(Conversation, conversation_id)
    assert conversation is not None
    assert conversation.user_id == test_user.id


def test_chat_endpoint_continues_existing_conversation(client, test_user, test_session, mock_agent_response):
    """Test chat endpoint continues existing conversation when conversation_id provided."""
    from app.models import Conversation

    token = create_jwt_token(test_user.id)

    # Create initial conversation
    with mock_agent_response("First response"):
        response1 = client.post(
            f"/api/{test_user.id}/chat",
            json={"query": "First query"},
            headers={"Authorization": f"Bearer {token}"}
        )

    conversation_id = response1.json()["conversation_id"]

    # Continue conversation
    with mock_agent_response("Second response"):
        response2 = client.post(
            f"/api/{test_user.id}/chat",
            json={
                "query": "Second query",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response2.status_code == 200
    assert response2.json()["conversation_id"] == conversation_id

    # Verify both messages are stored
    from app.models import Message
    from sqlmodel import select
    messages = test_session.exec(
        select(Message).where(Message.conversation_id == conversation_id)
    ).all()

    # Should have 4 messages: user1, assistant1, user2, assistant2
    assert len(messages) >= 4


def test_chat_endpoint_returns_404_for_nonexistent_conversation(client, test_user, mock_agent_response):
    """Test chat endpoint returns 404 when conversation_id doesn't exist."""
    token = create_jwt_token(test_user.id)

    with mock_agent_response():
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={
                "query": "Query",
                "conversation_id": 99999  # Non-existent
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_endpoint_returns_403_for_other_users_conversation(client, test_session, mock_agent_response):
    """Test chat endpoint returns 403 when trying to access another user's conversation."""
    from app.models import User, Conversation

    # Create two users
    user1 = User(email="user1@example.com", password_hash="hash1")
    user2 = User(email="user2@example.com", password_hash="hash2")
    test_session.add(user1)
    test_session.add(user2)
    test_session.commit()
    test_session.refresh(user1)
    test_session.refresh(user2)

    # Create conversation for user1
    conversation = Conversation(user_id=user1.id)
    test_session.add(conversation)
    test_session.commit()
    test_session.refresh(conversation)

    # Try to access user1's conversation with user2's token
    token = create_jwt_token(user2.id)

    with mock_agent_response():
        response = client.post(
            f"/api/{user2.id}/chat",
            json={
                "query": "Query",
                "conversation_id": conversation.id
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 403
    assert "does not belong" in response.json()["detail"].lower()


def test_chat_endpoint_stores_messages_in_database(client, test_user, test_session, mock_agent_response):
    """Test chat endpoint stores both user and assistant messages."""
    token = create_jwt_token(test_user.id)

    agent_response_text = "Task added successfully"

    with mock_agent_response(agent_response_text):
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"query": "Add task to buy groceries"},
            headers={"Authorization": f"Bearer {token}"}
        )

    conversation_id = response.json()["conversation_id"]

    # Verify messages stored
    from app.models import Message
    from sqlmodel import select
    messages = test_session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    assert len(messages) == 2

    # First message: user
    assert messages[0].role == "user"
    assert messages[0].content == "Add task to buy groceries"
    assert messages[0].user_id == test_user.id

    # Second message: assistant
    assert messages[1].role == "assistant"
    assert messages[1].content == agent_response_text
    assert messages[1].user_id == test_user.id


def test_chat_endpoint_handles_agent_errors_gracefully(client, test_user, test_session):
    """Test chat endpoint handles agent errors and returns friendly message."""
    token = create_jwt_token(test_user.id)

    # Mock agent to raise exception
    with patch('app.chat.run_agent') as mock_run_agent:
        mock_run_agent.side_effect = Exception("Simulated agent error")

        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"query": "Add task"},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200  # Still returns 200
    data = response.json()
    assert "apologize" in data["response"].lower() or "error" in data["response"].lower()


def test_chat_endpoint_passes_conversation_history_to_agent(client, test_user, test_session, mock_agent_response):
    """Test chat endpoint passes conversation history to agent for context."""
    from app.models import Conversation, Message

    token = create_jwt_token(test_user.id)

    # Create conversation with existing messages
    conversation = Conversation(user_id=test_user.id)
    test_session.add(conversation)
    test_session.commit()
    test_session.refresh(conversation)

    # Add previous messages
    msg1 = Message(
        conversation_id=conversation.id,
        user_id=test_user.id,
        role="user",
        content="Previous user message"
    )
    msg2 = Message(
        conversation_id=conversation.id,
        user_id=test_user.id,
        role="assistant",
        content="Previous assistant message"
    )
    test_session.add(msg1)
    test_session.add(msg2)
    test_session.commit()

    # Make request
    with patch('app.chat.run_agent') as mock_run_agent:
        mock_run_agent.return_value = "Response"

        response = client.post(
            f"/api/{test_user.id}/chat",
            json={
                "query": "New query",
                "conversation_id": conversation.id
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        # Verify agent was called with conversation history
        assert mock_run_agent.called
        call_args = mock_run_agent.call_args
        conversation_history = call_args.kwargs.get("conversation_history")

        assert conversation_history is not None
        assert len(conversation_history) >= 2
        assert conversation_history[0]["content"] == "Previous user message"
        assert conversation_history[1]["content"] == "Previous assistant message"
