---
name: error.user.friendly
description: "Transform technical errors into friendly, actionable messages that guide users toward resolution without exposing internal implementation details. Use when implementing error responses in API endpoints, handling AI agent failures, validating user inputs, or debugging production issues."
category: Error Handling / UX
complexity: Low
phase: 3
dependencies: ["FastAPI", "Pydantic"]
---

# Skill: User-Friendly Error Handling

**Category**: Error Handling / UX
**Complexity**: Low
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: FastAPI, Pydantic

## Purpose

Transform technical errors into friendly, actionable messages that guide users toward resolution without exposing internal implementation details.

## When to Use

- Implementing error responses in API endpoints
- Handling AI agent failures
- Validating user inputs
- Debugging production issues

## Pattern

### 1. Error Response Models

```python
# backend/app/models/errors.py
from pydantic import BaseModel
from typing import Optional, List

class ErrorDetail(BaseModel):
    """User-friendly error detail."""
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str
    details: List[ErrorDetail]
    request_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Unable to add task",
                "details": [
                    {
                        "message": "Task title is too long (max 200 characters)",
                        "field": "title",
                        "suggestion": "Try shortening your task description"
                    }
                ],
                "request_id": "abc-123"
            }
        }
```

### 2. Custom Exception Classes

```python
# backend/app/exceptions.py
from fastapi import HTTPException, status

class TaskError(HTTPException):
    """Base exception for task operations."""
    def __init__(self, detail: str, suggestion: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=self._format_error(detail, suggestion)
        )

    def _format_error(self, detail: str, suggestion: str) -> dict:
        return {
            "error": detail,
            "suggestion": suggestion,
            "type": "task_error"
        }

class TaskNotFoundError(TaskError):
    def __init__(self, task_id: int):
        super().__init__(
            detail=f"We couldn't find task #{task_id}",
            suggestion="Check your task list with 'Show my tasks' to see all tasks"
        )

class TaskLimitExceeded(TaskError):
    def __init__(self, limit: int):
        super().__init__(
            detail=f"You've reached the maximum of {limit} tasks",
            suggestion="Try completing or deleting some tasks first"
        )

class AgentError(HTTPException):
    """AI agent processing error."""
    def __init__(self, detail: str = "I'm having trouble processing that request"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": detail,
                "suggestion": "Try rephrasing your message or try again in a moment",
                "type": "agent_error"
            }
        )
```

### 3. Global Exception Handler

```python
# backend/app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import TaskError, AgentError
import logging
import uuid

app = FastAPI()
logger = logging.getLogger(__name__)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []

    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else None
        message = error["msg"]

        # Make message user-friendly
        if "field required" in message.lower():
            message = f"Please provide a {field}"
        elif "string too short" in message.lower():
            message = f"The {field} is too short"
        elif "string too long" in message.lower():
            message = f"The {field} is too long"

        errors.append({
            "message": message,
            "field": field,
            "suggestion": f"Check the {field} and try again"
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Please check your input",
            "details": errors,
            "request_id": str(uuid.uuid4())
        }
    )

@app.exception_handler(TaskError)
async def task_error_handler(request: Request, exc: TaskError):
    """Handle task-specific errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(AgentError)
async def agent_error_handler(request: Request, exc: AgentError):
    """Handle AI agent errors."""
    # Log for debugging
    logger.error(f"Agent error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    # Log technical details
    logger.error(f"Database error: {str(exc)}")

    # Return user-friendly message
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "We're having trouble connecting to the database",
            "suggestion": "Please try again in a moment",
            "type": "database_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors."""
    # Log full error for debugging
    logger.exception(f"Unexpected error: {str(exc)}")

    # Return generic user-friendly message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Something unexpected happened",
            "suggestion": "Please try again or contact support if the problem persists",
            "type": "internal_error",
            "request_id": str(uuid.uuid4())
        }
    )
```

### 4. AI Agent Error Wrapping

```python
# backend/app/services/agent_service.py
from app.exceptions import AgentError

async def safe_process_message(
    agent: Agent,
    message: str,
    conversation_history: List[Dict],
    user_id: str
) -> tuple[str, List[Dict]]:
    """Process message with friendly error handling."""

    # Input validation
    if not message or not message.strip():
        raise TaskError(
            detail="Please tell me what you'd like to do",
            suggestion="Try something like 'Add buy milk' or 'Show my tasks'"
        )

    if len(message) > 2000:
        raise TaskError(
            detail="Your message is too long",
            suggestion="Please keep messages under 2000 characters"
        )

    try:
        return await process_message(agent, message, conversation_history, user_id)

    except TimeoutError:
        raise AgentError(
            detail="That's taking longer than expected"
        )

    except ConnectionError:
        raise AgentError(
            detail="I'm having trouble connecting right now"
        )

    except Exception as e:
        # Log technical error
        logger.error(f"Agent processing error: {str(e)}")

        # Return friendly fallback
        raise AgentError()
```

### 5. Frontend Error Display

```typescript
// frontend/lib/error-handler.ts
interface ApiError {
  error: string;
  suggestion?: string;
  details?: Array<{
    message: string;
    field?: string;
    suggestion?: string;
  }>;
}

export function handleApiError(error: any): string {
  // Extract error from response
  if (error.response?.data) {
    const apiError: ApiError = error.response.data;

    // Build user-friendly message
    let message = apiError.error;

    if (apiError.suggestion) {
      message += `\n\n💡 ${apiError.suggestion}`;
    }

    if (apiError.details && apiError.details.length > 0) {
      message += '\n\nDetails:';
      apiError.details.forEach(detail => {
        message += `\n• ${detail.message}`;
        if (detail.suggestion) {
          message += ` (${detail.suggestion})`;
        }
      });
    }

    return message;
  }

  // Network error
  if (error.code === 'ERR_NETWORK') {
    return "Can't connect to the server. Please check your internet connection.";
  }

  // Timeout
  if (error.code === 'ECONNABORTED') {
    return "The request took too long. Please try again.";
  }

  // Generic fallback
  return "Something went wrong. Please try again.";
}

// Usage in component
async function sendMessage(message: string) {
  try {
    const response = await sendChatMessage(userId, message);
    // Handle success
  } catch (error) {
    const errorMessage = handleApiError(error);
    toast.error(errorMessage);  // Display to user
  }
}
```

## Error Message Guidelines

### ✓ Good Error Messages

- **Clear**: "Task title is too long (max 200 characters)"
- **Actionable**: "Try shortening your task description"
- **Friendly**: "We couldn't find that task"
- **Specific**: "Please provide a task title"

### ✗ Bad Error Messages

- **Technical**: "ValidationError: String length exceeds maximum"
- **Vague**: "An error occurred"
- **Blaming**: "You entered invalid data"
- **No guidance**: "Error 422"

## Acceptance Criteria

- [ ] All errors return user-friendly messages
- [ ] Technical details logged but not exposed to users
- [ ] Suggestions provided for common errors
- [ ] Consistent error response format
- [ ] HTTP status codes used correctly
- [ ] Request IDs included for tracking
- [ ] Frontend displays errors clearly
- [ ] No stack traces in production responses

## Common Error Scenarios

| Scenario | Status Code | User Message | Suggestion |
|----------|-------------|--------------|------------|
| Missing field | 422 | "Please provide a task title" | "Try 'Add [task name]'" |
| Task not found | 404 | "We couldn't find that task" | "Check your task list" |
| Auth failed | 401 | "Please log in again" | "Your session expired" |
| Rate limit | 429 | "Slow down a bit!" | "Wait a moment and try again" |
| Server error | 500 | "Something unexpected happened" | "Try again in a moment" |
| Timeout | 503 | "That's taking longer than expected" | "Try again" |

## Testing

```python
# test_error_handling.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_validation_error():
    response = client.post("/api/test-user/chat", json={})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert "details" in data
    assert "suggestion" in data["details"][0]

def test_task_not_found():
    response = client.get("/api/test-user/tasks/99999")
    assert response.status_code == 404
    data = response.json()
    assert "couldn't find" in data["error"].lower()
    assert data["suggestion"] is not None

def test_agent_error_handling():
    # Simulate agent failure
    response = client.post("/api/test-user/chat", json={
        "message": "x" * 3000  # Too long
    })
    assert response.status_code == 400
    data = response.json()
    assert "too long" in data["error"].lower()
```

## Monitoring

```python
# Log errors for analysis
import logging
from collections import defaultdict

error_counts = defaultdict(int)

def log_error(error_type: str, details: str):
    """Log errors for monitoring."""
    error_counts[error_type] += 1
    logging.error(f"{error_type}: {details}", extra={
        "error_type": error_type,
        "count": error_counts[error_type]
    })

    # Alert if error rate exceeds threshold
    if error_counts[error_type] > 100:
        alert_ops_team(error_type)
```

## References

- [HTTP Status Codes](https://httpstatuses.com/)
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- Phase 3 Spec: `specs/phase3/error-handling.md`
- Related Skills: `ai.agent.integration.md`, `nlp.command.parsing.md`

## Version

1.0.0 - Initial Phase 3 implementation
