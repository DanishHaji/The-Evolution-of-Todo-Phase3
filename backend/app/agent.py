"""AI Agent for Todo Chatbot using Cohere API.

This module integrates Cohere's command-r model with MCP tools for natural language
task management.
"""

from sqlmodel import Session
from typing import List, Dict, Optional
import os
import json
from dotenv import load_dotenv
import cohere

from app import mcp_tools

load_dotenv()

# Cohere configuration
COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY environment variable is required")

# Initialize Cohere client
cohere_client = cohere.Client(api_key=COHERE_API_KEY)

# System prompt for TodoAgent
SYSTEM_PROMPT = """You are a helpful Todo assistant that helps users manage their tasks through natural language.

IMPORTANT RULES:
1. User ID filtering is automatic - never ask user for their ID
2. Return tool results in natural, conversational language - NO raw JSON
3. If a tool raises ValueError, explain the error to the user in friendly terms
4. When listing tasks, present them in a clear, organized format
5. Always acknowledge successful operations with confirmation

BULK DELETE OPERATIONS:
For "delete all tasks" requests, you MUST:
1. First call list_tasks to get all tasks
2. Show user the list of tasks that will be deleted
3. After user confirms, DELETE EACH TASK ONE BY ONE by calling delete_task for each task ID
4. Confirm total number deleted at the end

EXAMPLES:
User: "Add task to buy groceries tomorrow"
You: "I'll add that task for you." → [call add_task] → "Done! I've added 'Buy groceries' to your tasks, due tomorrow."

User: "Delete task 123"
You: [call delete_task with task_id=123] → "Task 123 deleted successfully."

User: "Delete all my tasks"
You: [call list_tasks] → Shows list → "I found 3 tasks. Are you sure you want to delete all of them? This cannot be undone."
User: "yes"
You: [call delete_task for task 1] [call delete_task for task 2] [call delete_task for task 3] → "Done! I've deleted all 3 tasks."

User: "Show my high priority tasks"
You: [call list_tasks with priority="high"] → "You have 3 high priority tasks: 1. Buy groceries (due tomorrow), 2. Submit report (due Friday), 3. Call dentist (no due date)"

Remember: Be concise, friendly, and helpful. When user says 'yes' to confirm deletion, IMMEDIATELY proceed with deleting the tasks."""

# Define tools for Cohere
def get_cohere_tools():
    """Get tool definitions in Cohere format."""
    return [
        {
            "name": "add_task",
            "description": "Add a new todo task to the user's task list.",
            "parameter_definitions": {
                "title": {"description": "Task title", "type": "str", "required": True},
                "desc": {"description": "Task description", "type": "str", "required": False},
                "priority": {"description": "Priority level: low, medium, high", "type": "str", "required": False},
                "due_date": {"description": "Due date in ISO format", "type": "str", "required": False}
            }
        },
        {
            "name": "list_tasks",
            "description": "List tasks with optional filters.",
            "parameter_definitions": {
                "status": {"description": "Filter by completion status (true/false)", "type": "bool", "required": False},
                "priority": {"description": "Filter by priority", "type": "str", "required": False},
                "limit": {"description": "Maximum number of tasks", "type": "int", "required": False}
            }
        },
        {
            "name": "complete_task",
            "description": "Mark a task as complete.",
            "parameter_definitions": {
                "task_id": {"description": "ID of the task to complete", "type": "int", "required": True}
            }
        },
        {
            "name": "update_task",
            "description": "Update task fields.",
            "parameter_definitions": {
                "task_id": {"description": "Task ID", "type": "int", "required": True},
                "title": {"description": "New title", "type": "str", "required": False},
                "description": {"description": "New description", "type": "str", "required": False},
                "status": {"description": "Completion status", "type": "bool", "required": False}
            }
        },
        {
            "name": "delete_task",
            "description": "Delete a task.",
            "parameter_definitions": {
                "task_id": {"description": "ID of task to delete", "type": "int", "required": True}
            }
        },
        {
            "name": "search_tasks",
            "description": "Search tasks by keyword.",
            "parameter_definitions": {
                "query": {"description": "Search keyword", "type": "str", "required": True},
                "limit": {"description": "Max results", "type": "int", "required": False}
            }
        }
    ]


async def run_agent(
    query: str,
    user_id: int,
    db_session: Session,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Run the Todo agent with a user query.

    This is the main entry point for the chat API endpoint.

    Args:
        query: User's natural language query
        user_id: Authenticated user ID from JWT
        db_session: Database session for tool execution
        conversation_history: Optional previous messages for context

    Returns:
        Agent's natural language response

    Example:
        >>> response = await run_agent(
        ...     query="Add task to buy groceries",
        ...     user_id=1,
        ...     db_session=session
        ... )
        >>> print(response)
        "Done! I've added 'Buy groceries' to your tasks."
    """
    try:
        # Prepare message history for Cohere
        chat_history = []
        if conversation_history:
            for msg in conversation_history:
                chat_history.append({
                    "role": "USER" if msg["role"] == "user" else "CHATBOT",
                    "message": msg["content"]
                })

        # Get tool definitions
        tools = get_cohere_tools()

        # First call to Cohere with tools
        response = cohere_client.chat(
            model="command-nightly",
            message=query,
            chat_history=chat_history,
            preamble=SYSTEM_PROMPT,
            tools=tools,
            temperature=0.3
        )

        # Check if tools need to be called
        if response.tool_calls:
            tool_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call.name
                tool_params = tool_call.parameters

                # Execute the appropriate MCP tool
                try:
                    if tool_name == "add_task":
                        result = mcp_tools.add_task(
                            title=tool_params.get("title"),
                            desc=tool_params.get("desc", ""),
                            priority=tool_params.get("priority", "medium"),
                            tags=[],
                            due_date=tool_params.get("due_date"),
                            recurring=None,
                            session=db_session,
                            user_id=user_id
                        )
                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": f"Task created successfully with ID {result}"}]
                        })

                    elif tool_name == "list_tasks":
                        result = mcp_tools.list_tasks(
                            status=tool_params.get("status"),
                            priority=tool_params.get("priority"),
                            tags=None,
                            due_before=None,
                            due_after=None,
                            limit=tool_params.get("limit", 50),
                            session=db_session,
                            user_id=user_id
                        )
                        # Format tasks as readable text for Cohere
                        if result:
                            tasks_text = f"Found {len(result)} tasks:\n"
                            for task in result:
                                status_text = "[Done]" if task.get("status") else "[Pending]"
                                tasks_text += f"{status_text} ID: {task['id']} - {task['title']}"
                                if task.get('description'):
                                    tasks_text += f" ({task['description']})"
                                if task.get('priority'):
                                    tasks_text += f" [Priority: {task['priority']}]"
                                tasks_text += "\n"
                        else:
                            tasks_text = "No tasks found."

                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": tasks_text}]
                        })

                    elif tool_name == "complete_task":
                        result = mcp_tools.complete_task(
                            task_id=tool_params.get("task_id"),
                            session=db_session,
                            user_id=user_id
                        )
                        status_text = "completed" if result else "marked as incomplete"
                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": f"Task {tool_params.get('task_id')} {status_text} successfully"}]
                        })

                    elif tool_name == "update_task":
                        result = mcp_tools.update_task(
                            task_id=tool_params.get("task_id"),
                            title=tool_params.get("title"),
                            description=tool_params.get("description"),
                            priority=tool_params.get("priority"),
                            tags=None,
                            due_date=None,
                            status=tool_params.get("status"),
                            recurring=None,
                            session=db_session,
                            user_id=user_id
                        )
                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": f"Task {tool_params.get('task_id')} updated successfully. New details: {result.get('title', 'N/A')}"}]
                        })

                    elif tool_name == "delete_task":
                        result = mcp_tools.delete_task(
                            task_id=tool_params.get("task_id"),
                            session=db_session,
                            user_id=user_id
                        )
                        result_text = f"Task {tool_params.get('task_id')} deleted successfully" if result else f"Task {tool_params.get('task_id')} not found"
                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": result_text}]
                        })

                    elif tool_name == "search_tasks":
                        result = mcp_tools.search_tasks(
                            query=tool_params.get("query"),
                            limit=tool_params.get("limit", 20),
                            session=db_session,
                            user_id=user_id
                        )
                        # Format search results as readable text
                        if result:
                            search_text = f"Found {len(result)} tasks matching '{tool_params.get('query')}':\n"
                            for task in result:
                                status_text = "[Done]" if task.get("status") else "[Pending]"
                                search_text += f"{status_text} ID: {task['id']} - {task['title']}\n"
                        else:
                            search_text = f"No tasks found matching '{tool_params.get('query')}'"

                        tool_results.append({
                            "call": tool_call,
                            "outputs": [{"text": search_text}]
                        })

                except Exception as e:
                    print(f"[ERROR] Tool execution error: {tool_name} - {str(e)}")
                    tool_results.append({
                        "call": tool_call,
                        "outputs": [{"text": f"Error: {str(e)}"}]
                    })

            # Debug: Print tool results before sending to Cohere
            print(f"\n[DEBUG] Tool Results being sent to Cohere:")
            for i, tr in enumerate(tool_results):
                print(f"  Tool {i+1}: {tr['call'].name}")
                print(f"  Outputs: {tr['outputs']}")

            # Second call to Cohere with tool results
            final_response = cohere_client.chat(
                model="command-nightly",
                message="",
                chat_history=chat_history + [
                    {"role": "USER", "message": query},
                    {"role": "CHATBOT", "message": response.text, "tool_calls": response.tool_calls}
                ],
                preamble=SYSTEM_PROMPT,
                tools=tools,
                tool_results=tool_results,
                temperature=0.3
            )

            return final_response.text

        else:
            # No tools needed, return direct response
            return response.text

    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"
