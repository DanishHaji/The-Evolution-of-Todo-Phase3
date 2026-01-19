---
name: nlp.command.parsing
description: "Guide the AI agent to correctly interpret natural language commands and map them to the appropriate MCP tool invocations. Use when designing agent system prompts, testing command interpretation accuracy, debugging why agent selects wrong tool, or improving user experience with natural commands."
category: AI / NLP
complexity: Low-Medium
phase: 3
dependencies: ["OpenAI Agents SDK"]
---

# Skill: Natural Language Command Parsing

**Category**: AI / NLP
**Complexity**: Low-Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: OpenAI Agents SDK

## Purpose

Guide the AI agent to correctly interpret natural language commands and map them to the appropriate MCP tool invocations.

## When to Use

- Designing agent system prompts
- Testing command interpretation accuracy
- Debugging why agent selects wrong tool
- Improving user experience with natural commands

## Pattern

### 1. System Prompt Design

```python
# backend/app/services/agent_service.py

SYSTEM_PROMPT = """You are a helpful AI assistant for managing todo tasks.

## Your Capabilities

You can help users manage their todo lists through these operations:

### ADD TASK
When users say:
- "Add a task to..."
- "Create a task for..."
- "Remind me to..."
- "I need to..."
- "Don't let me forget to..."

Use the `add_task` tool with:
- title: The main task description (required)
- description: Additional details (optional)

Examples:
- "Add buy groceries" → add_task(title="Buy groceries")
- "Remind me to call mom tomorrow at 3pm" → add_task(title="Call mom", description="Tomorrow at 3pm")

### LIST TASKS
When users say:
- "Show me my tasks"
- "What do I have to do?"
- "List my todos"
- "What's on my list?"
- "Show pending tasks"
- "What did I complete?"

Use the `list_tasks` tool with:
- status: "all", "pending", or "completed"

Examples:
- "Show all tasks" → list_tasks(status="all")
- "What's pending?" → list_tasks(status="pending")
- "What have I done?" → list_tasks(status="completed")

### COMPLETE TASK
When users say:
- "Mark task X as done"
- "I finished task X"
- "Task X is complete"
- "Done with X"
- "Check off X"

Use the `complete_task` tool with:
- task_id: The task ID number

Examples:
- "Mark task 5 as done" → complete_task(task_id=5)
- "Finished grocery shopping" → First list_tasks to find ID, then complete_task

### DELETE TASK
When users say:
- "Delete task X"
- "Remove X"
- "Cancel X"
- "I don't need X anymore"
- "Forget about X"

Use the `delete_task` tool with:
- task_id: The task ID number

Examples:
- "Delete task 3" → delete_task(task_id=3)
- "Remove buy milk" → First list_tasks to find ID, then delete_task

### UPDATE TASK
When users say:
- "Change task X to..."
- "Update X"
- "Rename X"
- "Edit task X"

Use the `update_task` tool with:
- task_id: The task ID number
- title: New title (optional)
- description: New description (optional)

Examples:
- "Change task 1 to 'Call mom tonight'" → update_task(task_id=1, title="Call mom tonight")

## Important Rules

1. **Always confirm actions**: After completing a task operation, tell the user what you did
2. **Handle ambiguity**: If a task name is unclear, ask which task they mean
3. **Be conversational**: Don't just list JSON responses, speak naturally
4. **Multi-step operations**: If you need to find a task ID first, do it automatically
5. **Error handling**: If an operation fails, explain why in friendly terms

## Response Style

✓ Good: "I've added 'Buy groceries' to your list!"
✗ Bad: "Task created with ID 42"

✓ Good: "You have 3 pending tasks: Buy groceries, Call mom, and Finish report."
✗ Bad: "[{id: 1, title: 'Buy groceries'}, ...]"

✓ Good: "I marked 'Buy groceries' as complete. Great job!"
✗ Bad: "Task 1 completed successfully"

## Examples of Complex Commands

User: "Add a task to buy milk and eggs, and make sure I don't forget to call the dentist"
You: Should create TWO tasks:
1. add_task(title="Buy milk and eggs")
2. add_task(title="Call the dentist")

User: "What do I need to do today?"
You: list_tasks(status="pending") then format the response conversationally

User: "I'm done with the grocery shopping"
You:
1. list_tasks() to find the grocery task
2. complete_task(task_id=X) with the found ID
3. Confirm with the user

Remember: Be helpful, friendly, and natural!
"""
```

### 2. Command Pattern Examples

```python
# backend/app/services/nlp_patterns.py
from typing import Dict, List

# Common command patterns for agent training
COMMAND_PATTERNS = {
    "add_task": [
        "add {title}",
        "create {title}",
        "remind me to {title}",
        "i need to {title}",
        "don't forget {title}",
        "new task: {title}",
        "add task for {title}",
    ],

    "list_tasks": [
        "show my tasks",
        "what do i have",
        "list todos",
        "what's pending",
        "show completed",
        "what did i do",
        "my task list",
    ],

    "complete_task": [
        "done with {task}",
        "finished {task}",
        "mark {task} complete",
        "check off {task}",
        "completed {task}",
        "{task} is done",
    ],

    "delete_task": [
        "delete {task}",
        "remove {task}",
        "cancel {task}",
        "forget {task}",
        "don't need {task}",
    ],

    "update_task": [
        "change {task} to {new_value}",
        "update {task}",
        "rename {task}",
        "edit {task}",
    ]
}

# Ambiguous commands that need clarification
AMBIGUOUS_PATTERNS = [
    "delete that",  # Which task?
    "mark it done",  # Which task?
    "change it",  # Which task? To what?
    "add a task",  # What task?
]
```

### 3. Intent Detection (Optional Fallback)

```python
# backend/app/services/intent_detection.py
import re
from typing import Optional, Dict, Any

def detect_intent(message: str) -> Optional[Dict[str, Any]]:
    """
    Simple rule-based intent detection as fallback.

    Only use if agent fails to invoke correct tool.
    Prefer letting the agent handle interpretation.
    """
    message_lower = message.lower().strip()

    # Add task patterns
    if any(keyword in message_lower for keyword in ["add", "create", "remind", "new task"]):
        # Extract title
        for pattern in ["add (.*)", "create (.*)", "remind me to (.*)", "new task:? (.*)"]:
            match = re.search(pattern, message_lower)
            if match:
                return {
                    "intent": "add_task",
                    "entities": {"title": match.group(1).strip()}
                }

    # List tasks patterns
    if any(keyword in message_lower for keyword in ["show", "list", "what", "display"]):
        if "pending" in message_lower:
            return {"intent": "list_tasks", "entities": {"status": "pending"}}
        elif "completed" in message_lower or "done" in message_lower:
            return {"intent": "list_tasks", "entities": {"status": "completed"}}
        else:
            return {"intent": "list_tasks", "entities": {"status": "all"}}

    # Complete task patterns
    if any(keyword in message_lower for keyword in ["done", "finished", "complete", "check off"]):
        # Try to extract task ID
        match = re.search(r"task (\d+)", message_lower)
        if match:
            return {
                "intent": "complete_task",
                "entities": {"task_id": int(match.group(1))}
            }

    return None  # Let agent handle
```

## Acceptance Criteria

- [ ] Agent correctly interprets 90%+ of common commands
- [ ] Ambiguous commands trigger clarification requests
- [ ] Multi-task commands handled in single response
- [ ] Task ID extraction works for numeric references
- [ ] Natural language responses (not JSON dumps)
- [ ] Synonyms recognized (e.g., "todo" = "task")
- [ ] Context awareness (e.g., "mark it done" after listing tasks)

## Testing

```python
# test_nlp_commands.py
import pytest
from app.services.agent_service import create_agent, process_message

TEST_CASES = [
    # Add task
    ("Add buy milk", "add_task", {"title": "Buy milk"}),
    ("Remind me to call mom", "add_task", {"title": "Call mom"}),
    ("Create a task for dentist appointment", "add_task", {"title": "Dentist appointment"}),

    # List tasks
    ("Show my tasks", "list_tasks", {"status": "all"}),
    ("What's pending?", "list_tasks", {"status": "pending"}),
    ("What did I complete?", "list_tasks", {"status": "completed"}),

    # Complete task
    ("Mark task 5 as done", "complete_task", {"task_id": 5}),
    ("Finished task 3", "complete_task", {"task_id": 3}),

    # Delete task
    ("Delete task 2", "delete_task", {"task_id": 2}),
    ("Remove task 7", "delete_task", {"task_id": 7}),

    # Update task
    ("Change task 1 to 'Call John'", "update_task", {"task_id": 1, "title": "Call John"}),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("command,expected_tool,expected_args", TEST_CASES)
async def test_command_interpretation(command, expected_tool, expected_args):
    agent = create_agent()
    response, tools = await process_message(
        agent=agent,
        message=command,
        conversation_history=[],
        user_id="test-user"
    )

    assert len(tools) >= 1
    assert tools[0]["tool"] == expected_tool

    # Check arguments
    for key, value in expected_args.items():
        assert tools[0]["arguments"][key] == value
```

## Common Issues

1. **Agent doesn't invoke tool**:
   - Check system prompt clarity
   - Ensure tool descriptions are detailed
   - Verify MCP server is running

2. **Wrong tool selected**:
   - Refine tool descriptions
   - Add more examples in system prompt
   - Test with edge cases

3. **Missing parameters**:
   - Make required parameters clear in tool schema
   - Provide examples with all parameters

4. **Ambiguous handling**:
   - Train agent to ask clarifying questions
   - Provide context from conversation history

## Best Practices

1. **System Prompt**:
   - Clear, structured instructions
   - Many diverse examples
   - Explicit rules for edge cases

2. **Tool Descriptions**:
   - Detailed parameter explanations
   - Example invocations
   - When to use each tool

3. **Response Style**:
   - Natural, conversational
   - Confirm actions taken
   - Friendly error messages

4. **Context Management**:
   - Include recent conversation history
   - Reference previous messages
   - Maintain conversation flow

## References

- [OpenAI Prompt Engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- Phase 3 Spec: `specs/phase3/nlp-commands.md`
- Related Skills: `ai.agent.integration.md`, `error.user.friendly.md`

## Version

1.0.0 - Initial Phase 3 implementation
