---
name: agent-prompt-writer
description: "Craft effective system prompts for OpenAI agents that accurately parse natural language commands and invoke appropriate MCP tools. Use when designing new agent behaviors, debugging tool selection issues, improving command interpretation accuracy, or refining agent response quality."
category: AI / Prompt Engineering
complexity: Medium
phase: 3
dependencies: ["OpenAI Agents SDK", "MCP Tools"]
---

# Skill: Agent Prompt Writing

**Category**: AI / Prompt Engineering
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: OpenAI Agents SDK, MCP Tools

## Purpose

Craft effective system prompts for OpenAI agents that accurately parse natural language commands, invoke appropriate MCP tools, and provide helpful, conversational responses.

## When to Use

- Designing prompts for NL todo command handling
- Defining agent behavior and personality
- Improving tool selection accuracy
- Handling ambiguous user input
- Refining response tone and style
- Testing command interpretation
- Debugging incorrect tool invocations

## Pattern

### 1. Prompt Engineering Methodology

```python
# backend/app/prompts/base_template.py

"""
Prompt Engineering Process:
1. Define Role & Context
2. List Capabilities & Tools
3. Provide Command Patterns & Examples
4. Set Response Guidelines
5. Handle Edge Cases & Errors
6. Test & Iterate
"""

class PromptTemplate:
    """Base template for agent prompt construction."""

    def __init__(self):
        self.sections = {
            "role": "",
            "capabilities": [],
            "tools": {},
            "examples": [],
            "guidelines": [],
            "edge_cases": []
        }

    def build_prompt(self) -> str:
        """Construct full system prompt."""
        prompt = f"""
{self._build_role()}

{self._build_capabilities()}

{self._build_tools()}

{self._build_examples()}

{self._build_guidelines()}

{self._build_edge_cases()}
"""
        return prompt.strip()

    def _build_role(self) -> str:
        return f"# Role\n{self.sections['role']}"

    def _build_capabilities(self) -> str:
        caps = "\n".join([f"- {cap}" for cap in self.sections['capabilities']])
        return f"# Your Capabilities\n{caps}"

    def _build_tools(self) -> str:
        tools_text = []
        for tool_name, tool_info in self.sections['tools'].items():
            tools_text.append(f"""
### {tool_info['display_name']}
**When to use**: {tool_info['trigger_phrases']}
**Tool name**: `{tool_name}`
**Parameters**: {tool_info['parameters']}
**Examples**: {tool_info['examples']}
""")
        return "# Tools" + "\n".join(tools_text)

    def _build_examples(self) -> str:
        examples_text = "\n".join([
            f"- User: \"{ex['user']}\"\n  Action: {ex['action']}\n  Response: \"{ex['response']}\""
            for ex in self.sections['examples']
        ])
        return f"# Example Interactions\n{examples_text}"

    def _build_guidelines(self) -> str:
        guidelines = "\n".join([f"- {g}" for g in self.sections['guidelines']])
        return f"# Response Guidelines\n{guidelines}"

    def _build_edge_cases(self) -> str:
        cases = "\n".join([f"- {case}" for case in self.sections['edge_cases']])
        return f"# Edge Cases\n{cases}"
```

### 2. Todo Assistant Prompt Implementation

```python
# backend/app/prompts/todo_assistant.py
from app.prompts.base_template import PromptTemplate

def create_todo_assistant_prompt() -> str:
    """Create system prompt for Todo assistant agent."""

    template = PromptTemplate()

    # 1. Define Role
    template.sections['role'] = """
You are a helpful AI assistant for managing todo tasks. Your goal is to make task
management effortless through natural conversation. Be friendly, concise, and
proactive in helping users stay organized.
"""

    # 2. List Capabilities
    template.sections['capabilities'] = [
        "Add new tasks with titles and descriptions",
        "List tasks with filters (all, pending, completed)",
        "Mark tasks as complete",
        "Delete unwanted tasks",
        "Update existing task details",
        "Handle multiple operations in one request"
    ]

    # 3. Define Tools
    template.sections['tools'] = {
        "add_task": {
            "display_name": "ADD TASK",
            "trigger_phrases": "When users say: 'Add', 'Create', 'New task', 'Remind me', 'Don't forget', 'I need to'",
            "parameters": "title (required), description (optional)",
            "examples": [
                '"Add buy groceries" → add_task(title="Buy groceries")',
                '"Remind me to call mom tomorrow at 3pm" → add_task(title="Call mom", description="Tomorrow at 3pm")',
                '"Create a task for dentist appointment next week" → add_task(title="Dentist appointment", description="Next week")'
            ]
        },
        "list_tasks": {
            "display_name": "LIST TASKS",
            "trigger_phrases": "When users say: 'Show', 'List', 'What', 'Display', 'View', 'See'",
            "parameters": "status (optional: 'all', 'pending', 'completed')",
            "examples": [
                '"Show my tasks" → list_tasks(status="all")',
                '"What\'s pending?" → list_tasks(status="pending")',
                '"What did I complete today?" → list_tasks(status="completed")'
            ]
        },
        "complete_task": {
            "display_name": "COMPLETE TASK",
            "trigger_phrases": "When users say: 'Done', 'Finished', 'Complete', 'Check off', 'Mark as done'",
            "parameters": "task_id (required)",
            "examples": [
                '"Mark task 5 as done" → complete_task(task_id=5)',
                '"I finished the groceries" → list_tasks() first, then complete_task()',
                '"Done with task 3" → complete_task(task_id=3)'
            ]
        },
        "delete_task": {
            "display_name": "DELETE TASK",
            "trigger_phrases": "When users say: 'Delete', 'Remove', 'Cancel', 'Get rid of', 'Forget about'",
            "parameters": "task_id (required)",
            "examples": [
                '"Delete task 2" → delete_task(task_id=2)',
                '"Remove the meeting task" → list_tasks() first, then delete_task()',
                '"Cancel task 7" → delete_task(task_id=7)'
            ]
        },
        "update_task": {
            "display_name": "UPDATE TASK",
            "trigger_phrases": "When users say: 'Change', 'Update', 'Rename', 'Edit', 'Modify'",
            "parameters": "task_id (required), title (optional), description (optional)",
            "examples": [
                '"Change task 1 to Call John" → update_task(task_id=1, title="Call John")',
                '"Update the description of task 3" → update_task(task_id=3, description="...")',
                '"Rename task 5 to Buy milk" → update_task(task_id=5, title="Buy milk")'
            ]
        }
    }

    # 4. Provide Examples
    template.sections['examples'] = [
        {
            "user": "Add a task to buy milk and eggs",
            "action": "add_task(title='Buy milk and eggs')",
            "response": "I've added 'Buy milk and eggs' to your list!"
        },
        {
            "user": "What do I need to do today?",
            "action": "list_tasks(status='pending')",
            "response": "You have 3 pending tasks: 1. Buy groceries, 2. Call dentist, 3. Finish report."
        },
        {
            "user": "I'm done with the grocery shopping",
            "action": "list_tasks() → find grocery task → complete_task(task_id=X)",
            "response": "Great! I've marked 'Buy groceries' as complete. Well done!"
        },
        {
            "user": "Delete the meeting task and add a new one for tomorrow",
            "action": "list_tasks() → delete_task() → add_task()",
            "response": "I've removed the meeting task and added a new one for tomorrow."
        }
    ]

    # 5. Set Guidelines
    template.sections['guidelines'] = [
        "Always confirm actions taken (e.g., 'I've added...', 'Marked complete...')",
        "Be conversational and friendly, not robotic",
        "If task reference is ambiguous, list matching tasks and ask for clarification",
        "For multi-step operations, handle them automatically without asking for permission",
        "Format task lists in a readable way with numbers or bullets",
        "Use emojis sparingly (✅ for complete, ❌ for delete, ➕ for add)",
        "Keep responses concise but helpful",
        "If a command is unclear, ask ONE specific clarifying question",
        "Never expose raw JSON or technical errors to users"
    ]

    # 6. Handle Edge Cases
    template.sections['edge_cases'] = [
        "If user says 'mark it done' without context, ask which task",
        "If no tasks exist when listing, suggest adding one",
        "If task ID doesn't exist, say 'couldn't find that task' and offer to show all tasks",
        "If user adds duplicate task, confirm it's intentional or skip",
        "If task title is too long (>200 chars), ask user to shorten it",
        "If user tries to complete an already completed task, acknowledge it's already done",
        "Handle multi-sentence inputs by breaking into separate operations"
    ]

    return template.build_prompt()


# Usage
SYSTEM_PROMPT = create_todo_assistant_prompt()
```

### 3. Prompt Testing Framework

```python
# backend/tests/test_prompts.py
import pytest
from app.services.agent_service import create_agent, process_message

class PromptTestCase:
    """Test case for prompt evaluation."""
    def __init__(self, input_text: str, expected_tool: str, expected_args: dict):
        self.input = input_text
        self.expected_tool = expected_tool
        self.expected_args = expected_args

# Test Suite
PROMPT_TEST_CASES = [
    # ADD TASK variations
    PromptTestCase("Add buy groceries", "add_task", {"title": "buy groceries"}),
    PromptTestCase("Remind me to call mom", "add_task", {"title": "call mom"}),
    PromptTestCase("I need to finish the report", "add_task", {"title": "finish the report"}),
    PromptTestCase("Don't let me forget about the dentist", "add_task", {"title": "dentist"}),

    # LIST TASK variations
    PromptTestCase("Show my tasks", "list_tasks", {"status": "all"}),
    PromptTestCase("What's pending?", "list_tasks", {"status": "pending"}),
    PromptTestCase("What did I complete?", "list_tasks", {"status": "completed"}),

    # COMPLETE TASK variations
    PromptTestCase("Mark task 5 as done", "complete_task", {"task_id": 5}),
    PromptTestCase("I finished task 3", "complete_task", {"task_id": 3}),
    PromptTestCase("Done with the groceries", "list_tasks", {}),  # Should list first

    # DELETE TASK variations
    PromptTestCase("Delete task 2", "delete_task", {"task_id": 2}),
    PromptTestCase("Remove the meeting", "list_tasks", {}),  # Should list first

    # UPDATE TASK variations
    PromptTestCase("Change task 1 to Call John", "update_task", {"task_id": 1, "title": "Call John"}),

    # EDGE CASES
    PromptTestCase("mark it done", "clarification_needed", {}),  # Ambiguous
    PromptTestCase("delete that task", "clarification_needed", {}),  # Ambiguous
    PromptTestCase("Add task to buy milk and add another for dentist", "add_task", {}),  # Multiple ops
]

@pytest.mark.asyncio
async def test_prompt_accuracy():
    """Test prompt accuracy across all test cases."""
    agent = create_agent()
    results = []

    for test_case in PROMPT_TEST_CASES:
        response, tool_calls = await process_message(
            agent=agent,
            message=test_case.input,
            conversation_history=[],
            user_id="test-user"
        )

        # Check if correct tool was invoked
        if tool_calls:
            actual_tool = tool_calls[0]["tool"]
            passed = actual_tool == test_case.expected_tool
        else:
            passed = test_case.expected_tool == "clarification_needed"

        results.append({
            "input": test_case.input,
            "expected": test_case.expected_tool,
            "actual": tool_calls[0]["tool"] if tool_calls else None,
            "passed": passed
        })

    # Calculate accuracy
    accuracy = sum(r["passed"] for r in results) / len(results)
    print(f"Prompt Accuracy: {accuracy * 100:.1f}%")

    # Print failures
    failures = [r for r in results if not r["passed"]]
    if failures:
        print("\nFailed cases:")
        for failure in failures:
            print(f"  Input: {failure['input']}")
            print(f"  Expected: {failure['expected']}, Got: {failure['actual']}")

    assert accuracy >= 0.90, f"Prompt accuracy {accuracy:.1%} below 90% threshold"
```

### 4. Prompt Refinement Process

```python
# backend/scripts/refine_prompt.py
from typing import List, Dict
import json

class PromptRefiner:
    """Iteratively refine prompts based on test results."""

    def __init__(self, base_prompt: str):
        self.base_prompt = base_prompt
        self.iterations = []

    def analyze_failures(self, test_results: List[Dict]) -> Dict[str, List[str]]:
        """Analyze test failures and categorize issues."""
        issues = {
            "wrong_tool": [],
            "missing_params": [],
            "no_tool_invoked": [],
            "incorrect_clarification": []
        }

        for result in test_results:
            if not result["passed"]:
                if result["actual"] is None:
                    issues["no_tool_invoked"].append(result["input"])
                elif result["actual"] != result["expected"]:
                    issues["wrong_tool"].append(result["input"])

        return issues

    def suggest_improvements(self, issues: Dict[str, List[str]]) -> List[str]:
        """Suggest prompt improvements based on issues."""
        suggestions = []

        if issues["wrong_tool"]:
            suggestions.append(
                "Add more trigger phrase examples for misclassified commands"
            )
            suggestions.append(
                "Increase distinction between similar tools (e.g., complete vs delete)"
            )

        if issues["missing_params"]:
            suggestions.append(
                "Emphasize required parameters in tool descriptions"
            )

        if issues["no_tool_invoked"]:
            suggestions.append(
                "Strengthen tool invocation instructions"
            )
            suggestions.append(
                "Add examples of when to invoke each tool"
            )

        if issues["incorrect_clarification"]:
            suggestions.append(
                "Refine ambiguity detection rules"
            )
            suggestions.append(
                "Add guidelines for when to ask vs assume"
            )

        return suggestions

    def apply_refinement(self, improvements: List[str]) -> str:
        """Apply improvements to prompt."""
        # This would be manual in practice
        refined_prompt = self.base_prompt

        for improvement in improvements:
            print(f"📝 Apply: {improvement}")
            # Manual editing based on suggestion

        return refined_prompt

    def evaluate_iteration(self, accuracy: float) -> bool:
        """Check if refinement improved accuracy."""
        if not self.iterations:
            self.iterations.append(accuracy)
            return False

        improved = accuracy > self.iterations[-1]
        self.iterations.append(accuracy)
        return improved


# Usage
refiner = PromptRefiner(base_prompt=SYSTEM_PROMPT)
test_results = run_tests()  # Run test suite
issues = refiner.analyze_failures(test_results)
suggestions = refiner.suggest_improvements(issues)

print("🔍 Issues Found:")
for category, examples in issues.items():
    if examples:
        print(f"\n{category}:")
        for ex in examples[:3]:  # Show first 3
            print(f"  - {ex}")

print("\n💡 Suggested Improvements:")
for suggestion in suggestions:
    print(f"  - {suggestion}")
```

### 5. Response Quality Guidelines

```python
# backend/app/prompts/response_guidelines.py

RESPONSE_PATTERNS = {
    "add_task": [
        "✅ I've added '{title}' to your list!",
        "✅ Added: {title}",
        "✅ Got it! '{title}' is now on your list.",
    ],

    "complete_task": [
        "✅ Marked '{title}' as complete. Great job!",
        "✅ '{title}' is done! Well done!",
        "✅ Completed: {title}",
    ],

    "delete_task": [
        "❌ Removed '{title}' from your list.",
        "❌ Deleted: {title}",
        "❌ '{title}' is gone.",
    ],

    "list_tasks": {
        "empty": "You don't have any tasks yet. Want to add one?",
        "format": """
You have {count} {status} task(s):
{task_list}
""",
    },

    "clarification": [
        "Which task did you mean? Here's your list:\n{task_list}",
        "I found multiple matches. Can you be more specific?",
        "Could you clarify which task? You have:\n{task_list}",
    ],

    "error": [
        "Hmm, I couldn't find that task. Want to see your full list?",
        "Something went wrong. Could you try rephrasing?",
        "I didn't quite catch that. Could you try again?",
    ]
}

def format_response(tool: str, result: dict, context: dict = None) -> str:
    """Format agent response based on tool and result."""
    import random

    if tool == "add_task":
        template = random.choice(RESPONSE_PATTERNS["add_task"])
        return template.format(title=result.get("title", "task"))

    elif tool == "complete_task":
        template = random.choice(RESPONSE_PATTERNS["complete_task"])
        return template.format(title=result.get("title", "task"))

    elif tool == "list_tasks":
        tasks = result.get("tasks", [])
        if not tasks:
            return RESPONSE_PATTERNS["list_tasks"]["empty"]

        task_list = "\n".join([
            f"{i+1}. {'✅' if t['completed'] else '⭕'} {t['title']}"
            for i, t in enumerate(tasks)
        ])

        return RESPONSE_PATTERNS["list_tasks"]["format"].format(
            count=len(tasks),
            status=context.get("status", ""),
            task_list=task_list
        )

    return "Done!"
```

## Acceptance Criteria

- [ ] Agent invokes correct tool for 90%+ of common commands
- [ ] Tool parameters are extracted accurately
- [ ] Ambiguous commands trigger clarification requests
- [ ] Responses are conversational and user-friendly
- [ ] Multi-operation commands handled correctly
- [ ] Edge cases (empty list, invalid ID) handled gracefully
- [ ] Prompt is maintainable and easy to update
- [ ] Test suite covers all tool variations

## Quality Criteria

### Prompt Quality
- **Clarity**: Instructions are unambiguous
- **Completeness**: All tools and scenarios covered
- **Conciseness**: No unnecessary verbosity
- **Testability**: Clear success criteria

### Response Quality
- **Accuracy**: Correct tool selected and invoked
- **Tone**: Friendly, helpful, conversational
- **Formatting**: Easy to read and scan
- **Consistency**: Similar commands get similar responses

### Tool Selection
- **Precision**: Right tool for the command
- **Recall**: Commands trigger tool invocations
- **Disambiguation**: Asks when truly ambiguous

## Testing Strategy

```python
# Test Categories
TESTS = {
    "basic_commands": [
        # Simple, clear commands for each tool
    ],

    "variations": [
        # Different phrasings for same intent
    ],

    "edge_cases": [
        # Ambiguous, incomplete, or unusual commands
    ],

    "multi_operation": [
        # Multiple tasks in one command
    ],

    "context_dependent": [
        # Commands that need conversation history
    ]
}
```

## Common Issues

1. **Tool Confusion**: Agent selects wrong tool
   - **Fix**: Add more distinctive trigger phrases
   - **Fix**: Include negative examples ("NOT for...")

2. **Missing Parameters**: Tool invoked without required params
   - **Fix**: Emphasize required vs optional parameters
   - **Fix**: Show complete examples with all params

3. **Over-clarification**: Agent asks when it should proceed
   - **Fix**: Add guidelines for when to ask vs assume
   - **Fix**: Reduce ambiguity triggers

4. **Under-clarification**: Agent assumes when it should ask
   - **Fix**: Strengthen ambiguity detection rules
   - **Fix**: Add more ambiguous examples

5. **Robotic Responses**: Outputs sound unnatural
   - **Fix**: Add personality guidelines
   - **Fix**: Provide varied response templates

## Best Practices

1. **Start Simple**: Basic prompt → test → iterate
2. **Use Examples**: Show don't tell (3-5 examples per tool)
3. **Define Edge Cases**: Explicitly handle ambiguity
4. **Test Continuously**: Run test suite after each change
5. **Version Control**: Track prompt iterations
6. **Monitor Production**: Log misclassifications
7. **Gather Feedback**: Real user interactions
8. **Refine Iteratively**: Small improvements over time

## Prompt Versioning

```python
# backend/app/prompts/versions.py
PROMPT_VERSIONS = {
    "v1.0.0": "Initial prompt with basic tool descriptions",
    "v1.1.0": "Added trigger phrase examples",
    "v1.2.0": "Improved edge case handling",
    "v1.3.0": "Enhanced response tone guidelines",
    "v2.0.0": "Complete rewrite with structured sections",
}

CURRENT_VERSION = "v2.0.0"
```

## References

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Few-Shot Learning](https://arxiv.org/abs/2005.14165)
- Phase 3 Spec: `specs/phase3/agent-prompts.md`
- Related Skills: `nlp.command.parsing.md`, `ai.agent.integration.md`

## Version

1.0.0 - Initial Phase 3 implementation
