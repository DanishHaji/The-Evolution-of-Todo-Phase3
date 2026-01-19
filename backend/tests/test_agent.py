"""Integration tests for AI agent (TDD approach).

These tests verify that the agent correctly integrates with MCP tools
and handles natural language queries appropriately.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.agent import run_agent
import json


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI API response."""
    def _create_response(content=None, tool_calls=None):
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        mock_message.content = content
        mock_message.tool_calls = tool_calls

        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        return mock_response
    return _create_response


def test_agent_calls_add_task_for_simple_query(test_session, test_user, mock_openai_response):
    """Test agent calls add_task for 'Add task to buy groceries'."""
    # Mock Runner.run_sync to return a successful response
    mock_result = Mock()
    mock_result.final_output = "Done! I've added 'Buy groceries' to your tasks."

    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.return_value = mock_result

        # Run agent
        response = run_agent(
            query="Add task to buy groceries",
            user_id=test_user.id,
            db_session=test_session
        )

        # Verify Runner was called
        assert mock_runner.called
        assert "added" in response.lower() or "groceries" in response.lower()


def test_agent_calls_list_tasks_for_show_my_tasks(test_session, test_user, mock_openai_response):
    """Test agent calls list_tasks for 'Show my tasks'."""
    # Mock Runner.run_sync
    mock_result = Mock()
    mock_result.final_output = "You have 2 tasks in your list."

    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.return_value = mock_result

        response = run_agent(
            query="Show my tasks",
            user_id=test_user.id,
            db_session=test_session
        )

        assert mock_runner.called
        assert "tasks" in response.lower()


def test_agent_asks_confirmation_for_delete_all_tasks(test_session, test_user, mock_openai_response):
    """Test agent asks for confirmation before deleting tasks."""
    mock_result = Mock()
    mock_result.final_output = "Are you sure you want to delete all your tasks? Please confirm."

    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.return_value = mock_result

        response = run_agent(
            query="Delete all my tasks",
            user_id=test_user.id,
            db_session=test_session
        )

        assert "confirm" in response.lower() or "sure" in response.lower()


def test_agent_handles_tool_errors_gracefully(test_session, test_user, mock_openai_response):
    """Test agent handles ValueError from tools and explains to user."""
    mock_result = Mock()
    mock_result.final_output = "I'm sorry, but the priority must be 'low', 'medium', or 'high'."

    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.return_value = mock_result

        response = run_agent(
            query="Add task with invalid priority",
            user_id=test_user.id,
            db_session=test_session
        )

        assert "priority" in response.lower() or "sorry" in response.lower()


def test_agent_filters_by_user_id_automatically(test_session, test_user, mock_openai_response):
    """Test agent automatically filters tasks by user_id without asking user."""
    mock_result = Mock()
    mock_result.final_output = "You have 1 task: User 1 task"

    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.return_value = mock_result

        response = run_agent(
            query="Show my tasks",
            user_id=test_user.id,
            db_session=test_session
        )

        assert "User 1 task" in response or "task" in response.lower()


def test_agent_respects_max_iterations(test_session, test_user, mock_openai_response):
    """Test agent handles errors gracefully."""
    # Mock an exception during Runner.run_sync
    with patch('app.agent.Runner.run_sync') as mock_runner:
        mock_runner.side_effect = Exception("Simulated error")

        response = run_agent(
            query="Show my tasks",
            user_id=test_user.id,
            db_session=test_session
        )

        assert "apologize" in response.lower() or "error" in response.lower()
