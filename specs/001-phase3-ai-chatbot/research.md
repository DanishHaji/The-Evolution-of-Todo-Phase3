# Research: AI-Powered Todo Chatbot - Phase 3

**Feature**: 001-phase3-ai-chatbot
**Date**: 2026-01-16
**Phase**: 0 - Technology Research and Decisions

## Purpose

This document consolidates research findings and technology decisions for Phase 3 implementation. All "NEEDS CLARIFICATION" items from Technical Context have been resolved through research and evaluation of alternatives.

## Technology Decisions

### 1. AI Model Provider: Cohere API (command-r)

**Decision**: Use Cohere API with command-r model instead of Google Gemini

**Rationale**:
- **Enhanced NL Understanding**: Cohere command-r specifically optimized for chat and command interpretation
- **Better Tool Calling**: Native support for function calling with structured outputs
- **Cost Efficiency**: Cohere's pricing more competitive for high-volume chat interactions
- **API Compatibility**: Cohere API compatible with OpenAI client format (drop-in replacement)
- **Multilingual Support**: Built-in support for Urdu and other languages (bonus requirement)
- **Context Window**: 8K tokens sufficient for conversation history + tool definitions

**Alternatives Considered**:
- **Google Gemini**: Good but requires different SDK integration, pricing less predictable
- **OpenAI GPT-4**: Excellent but expensive, overkill for task management commands
- **Claude**: Strong reasoning but API rate limits restrictive for real-time chat

**Implementation**:
```python
from agents import AsyncOpenAI, OpenAIChatCompletionsModel

cohere_client = AsyncOpenAI(
    api_key=os.environ["COHERE_API_KEY"],
    base_url="https://api.cohere.ai/v1"
)

model = OpenAIChatCompletionsModel(
    model="command-r",
    openai_client=cohere_client
)
```

**References**:
- Cohere Docs: https://docs.cohere.com/docs/command-r
- OpenAI Agents SDK Compatibility: https://github.com/openai/swarm

---

### 2. Package Manager: UV for Python

**Decision**: Use UV instead of pip/poetry for backend dependency management

**Rationale**:
- **Speed**: 10-100x faster than pip for dependency resolution
- **Reliability**: Consistent lock files prevent dependency conflicts
- **Simplicity**: Single command for add/remove/install operations
- **Modern**: Built in Rust, actively maintained by Astral (ruff creators)
- **Developer Experience**: Better error messages, faster CI/CD

**Alternatives Considered**:
- **pip + requirements.txt**: Slow, no lock file, manual version pinning
- **poetry**: Better than pip but slower than UV, more complex configuration
- **pipenv**: Abandoned project, not recommended for new projects

**Implementation**:
```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Usage
uv add fastapi uvicorn sqlmodel psycopg2-binary
uv add agents cohere python-dotenv pydantic
uv add --dev pytest pytest-asyncio httpx black isort mypy

# Running
uv run python main.py
uv run pytest
```

**References**:
- UV Docs: https://docs.astral.sh/uv/
- UV vs Poetry Benchmark: https://astral.sh/blog/uv-performance

---

### 3. ORM: SQLModel for Type-Safe Database Operations

**Decision**: Use SQLModel instead of SQLAlchemy or Django ORM

**Rationale**:
- **Type Safety**: Built on Pydantic, full mypy support for compile-time checks
- **DX**: Single model definition for both DB schema and API validation
- **FastAPI Integration**: Native support, automatic OpenAPI schema generation
- **Simplicity**: Less boilerplate than SQLAlchemy, easier to learn
- **Async Support**: Compatible with asyncpg for async database operations
- **Migrations**: Works with Alembic for schema versioning

**Alternatives Considered**:
- **SQLAlchemy Core**: More control but verbose, no automatic validation
- **Django ORM**: Excellent but tied to Django framework (overkill)
- **Tortoise ORM**: Async-first but smaller community, less mature

**Implementation**:
```python
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional, List
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: str = ""
    priority: str = "medium"
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = None
    status: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

engine = create_engine(os.environ["DATABASE_URL"])
SQLModel.metadata.create_all(engine)
```

**References**:
- SQLModel Docs: https://sqlmodel.tiangolo.com/
- FastAPI + SQLModel Tutorial: https://fastapi.tiangolo.com/tutorial/sql-databases/

---

### 4. MCP SDK: Official Python MCP SDK

**Decision**: Use Official MCP SDK for tool definitions

**Rationale**:
- **Standard Protocol**: Ensures compatibility with OpenAI Agents SDK
- **Stateless Design**: Tools designed for stateless invocation (aligns with constitution)
- **Type Safety**: Full type hints for tool parameters and return values
- **Documentation**: Auto-generated tool descriptions for agent context
- **Flexibility**: Easy to extend with custom tools

**Alternatives Considered**:
- **Custom Tool Implementation**: More control but reinventing the wheel, no standard
- **LangChain Tools**: Heavy framework, includes unnecessary abstractions

**Implementation**:
```python
from agents import function_tool
from sqlmodel import Session, select

@function_tool
def add_task(
    title: str,
    desc: str = "",
    priority: str = "medium",
    tags: List[str] = [],
    due_date: Optional[str] = None,
    session: Session = None,
    user_id: int = None
) -> int:
    """Add a new Todo task to the database.

    Args:
        title: Task title (required)
        desc: Task description (optional)
        priority: Priority level (low/medium/high)
        tags: List of tags for organization
        due_date: ISO format date string (YYYY-MM-DD)
        session: Database session (injected by FastAPI)
        user_id: Authenticated user ID (injected by middleware)

    Returns:
        Task ID of created task
    """
    task = Task(
        user_id=user_id,
        title=title,
        description=desc,
        priority=priority,
        tags=tags,
        due_date=datetime.fromisoformat(due_date) if due_date else None
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task.id
```

**References**:
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- OpenAI Agents Function Tools: https://github.com/openai/swarm#function-tools

---

### 5. Frontend Chat UI: OpenAI ChatKit

**Decision**: Use OpenAI ChatKit for chat interface

**Rationale**:
- **Purpose-Built**: Designed specifically for AI chat applications
- **Rich Features**: Message history, typing indicators, file uploads, reactions
- **Customizable**: Theming with Tailwind CSS classes
- **Accessible**: WCAG 2.1 compliant out-of-the-box
- **Mobile-Responsive**: Works on all screen sizes
- **SSR Compatible**: Works with Next.js App Router

**Alternatives Considered**:
- **Custom React Chat**: Full control but 2-3 weeks development time
- **ChatUI by Alibaba**: Good but less documentation, Chinese-first
- **react-chat-elements**: Lightweight but missing features (typing indicators, reactions)

**Implementation**:
```tsx
import { ChatKit } from '@openai/chatkit';
import { useAuth } from 'better-auth/react';
import { useState } from 'react';

export function ChatbotModal() {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (query: string) => {
    const response = await fetch(`/api/${user.id}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });
    const data = await response.json();
    setMessages([...messages, { role: 'user', content: query }, { role: 'assistant', content: data.response }]);
  };

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      placeholder="Ask me anything about your todos..."
      theme="dark"
    />
  );
}
```

**References**:
- OpenAI ChatKit: https://platform.openai.com/docs/chatkit
- Next.js Integration: https://platform.openai.com/docs/chatkit/nextjs

---

### 6. Authentication: Better Auth + JWT

**Decision**: Use Better Auth for authentication with JWT tokens

**Rationale**:
- **Modern**: Built for Next.js App Router, supports server actions
- **Flexible**: Works with any backend (FastAPI in our case)
- **Secure**: bcrypt password hashing, CSRF protection, secure cookies
- **JWT Support**: Native JWT token generation with configurable expiry
- **TypeScript-First**: Full type safety for auth context
- **Extensible**: Easy to add OAuth providers later

**Alternatives Considered**:
- **NextAuth.js**: Excellent but overkill for simple JWT, tied to Next.js pages router
- **Auth0**: Powerful but expensive, requires external service
- **Custom JWT**: Secure but reinventing the wheel, missing features (refresh tokens, CSRF)

**Implementation**:

**Frontend (Next.js)**:
```tsx
import { BetterAuth } from 'better-auth/react';

export const authClient = new BetterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  credentials: {
    username: true,
    password: true
  },
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET,
    expiresIn: '7d'
  }
});

// Usage in components
const { user, token, login, logout } = useAuth();
```

**Backend (FastAPI)**:
```python
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt
from datetime import datetime, timedelta

JWT_SECRET = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"

def verify_jwt(authorization: str = Header(...)) -> int:
    """Verify JWT token and return user_id."""
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/{user_id}/chat")
async def chat(
    user_id: int,
    query: str,
    authenticated_user_id: int = Depends(verify_jwt)
):
    if user_id != authenticated_user_id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Process chat...
```

**References**:
- Better Auth: https://www.better-auth.com/docs
- FastAPI JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

---

### 7. Database: Neon PostgreSQL

**Decision**: Use Neon Serverless PostgreSQL

**Rationale**:
- **Serverless**: Auto-scaling, pay-per-use (cost-effective for hackathon)
- **PostgreSQL**: Full feature set (JSON columns, foreign keys, transactions)
- **Developer Experience**: Instant provisioning, branching for testing
- **Performance**: Connection pooling built-in, fast queries
- **Free Tier**: Generous limits for development and demo
- **Compatibility**: Works with SQLModel, psycopg2, asyncpg

**Alternatives Considered**:
- **Supabase**: Similar but more opinionated, includes auth (redundant with Better Auth)
- **PlanetScale**: MySQL-based, lacks PostgreSQL features (JSON queries)
- **Self-Hosted PostgreSQL**: More control but requires infrastructure management

**Implementation**:
```python
from sqlmodel import create_engine, Session

DATABASE_URL = os.environ["DATABASE_URL"]
# Format: postgresql://user:password@host.neon.tech/dbname?sslmode=require

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)

def get_session():
    with Session(engine) as session:
        yield session
```

**References**:
- Neon Docs: https://neon.tech/docs/introduction
- SQLModel + Neon: https://neon.tech/docs/guides/sqlmodel

---

### 8. Testing Framework: pytest + Playwright

**Decision**: Use pytest for backend, Playwright for E2E

**Rationale**:

**pytest**:
- **Standard**: De facto Python testing framework
- **Fixtures**: Dependency injection for test setup (DB sessions, mock data)
- **Async Support**: pytest-asyncio for testing FastAPI endpoints
- **Coverage**: pytest-cov for code coverage reports
- **FastAPI Integration**: httpx TestClient for API testing

**Playwright**:
- **Cross-Browser**: Tests on Chrome, Firefox, Safari
- **E2E**: Real browser automation, tests entire stack
- **Reliable**: Auto-waiting for elements, retry logic
- **Debugging**: Screenshots, video recording, trace viewer
- **TypeScript**: Type-safe test authoring

**Alternatives Considered**:
- **unittest**: Built-in but verbose, less features
- **Selenium**: Older, slower, more flaky than Playwright
- **Cypress**: Great but JavaScript-only, slower than Playwright

**Implementation**:

**Backend (pytest)**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from main import app

@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield TestClient(app)

def test_add_task(client):
    response = client.post("/api/1/chat", json={"query": "Add task to buy milk"})
    assert response.status_code == 200
    assert "buy milk" in response.json()["response"].lower()
```

**Frontend (Playwright)**:
```typescript
import { test, expect } from '@playwright/test';

test('user can add task via chatbot', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('[data-testid="chat-icon"]');
  await page.fill('[data-testid="chat-input"]', 'Add task to buy groceries');
  await page.press('[data-testid="chat-input"]', 'Enter');
  await expect(page.locator('text=buy groceries')).toBeVisible();
});
```

**References**:
- pytest: https://docs.pytest.org/
- Playwright: https://playwright.dev/docs/intro

---

## Architecture Patterns

### Stateless Design Pattern

**Decision**: Implement fully stateless backend architecture

**Rationale**:
- **Constitution Requirement**: Stateless Architecture (Principle I)
- **Scalability**: Enables horizontal scaling without sticky sessions
- **Kubernetes-Ready**: Pods can be killed/restarted without data loss
- **Performance**: No session synchronization overhead
- **Simplicity**: Easier to debug and test

**Implementation**:
- All conversation state stored in PostgreSQL (Conversation/Message tables)
- JWT tokens carry user identity (no server-side sessions)
- MCP tools receive DB session as parameter (no global state)
- FastAPI dependency injection for database sessions

**References**:
- 12-Factor App: https://12factor.net/processes
- Stateless Authentication: https://jwt.io/introduction

---

### Natural Language Processing Pattern

**Decision**: Agent-based NL processing with explicit tool calling

**Rationale**:
- **Clarity**: Agent explicitly calls tools (add_task, delete_task) instead of generating SQL
- **Safety**: Agent can't execute arbitrary code, only predefined tools
- **Auditability**: All tool calls logged for debugging and compliance
- **Confirmations**: Agent can ask user confirmation before destructive actions

**Implementation Flow**:
1. User sends NL query: "Add task to buy groceries tomorrow"
2. FastAPI receives query, loads conversation history
3. OpenAI Agents SDK + Cohere parses NL intent
4. Agent selects `add_task` tool with parameters: `{title: "Buy groceries", due_date: "2026-01-17"}`
5. MCP tool executes database operation with user_id filtering
6. Agent receives task_id, generates confirmation message
7. FastAPI persists exchange to database, returns response

**Error Handling**:
- **Ambiguous Query**: Agent responds with clarifying question
- **Invalid Parameters**: Pydantic validation raises 400 error
- **Database Error**: Catch exception, log error, return user-friendly message
- **JWT Invalid**: Middleware raises 401 before reaching agent

**References**:
- OpenAI Agents SDK: https://github.com/openai/swarm
- Function Calling Best Practices: https://docs.cohere.com/docs/tools

---

## Performance Optimization Strategies

### 1. Database Connection Pooling
- **Strategy**: SQLModel engine with pool_size=10, max_overflow=20
- **Benefit**: Reuse connections, reduce connection overhead
- **Implementation**: Configured in engine creation

### 2. Query Optimization
- **Strategy**: Add indexes on user_id, created_at columns
- **Benefit**: Fast filtering and sorting
- **Implementation**: SQLModel Field(index=True)

### 3. Conversation History Pruning
- **Strategy**: Load last 50 messages only, paginate older messages
- **Benefit**: Reduce agent context size, faster processing
- **Implementation**: Query with LIMIT 50 ORDER BY created_at DESC

### 4. Caching (Future Enhancement)
- **Strategy**: Redis cache for frequently accessed tasks
- **Benefit**: Reduce database load
- **Implementation**: Not in Phase 3 scope, add in Phase 4

---

## Security Best Practices

### 1. JWT Token Security
- **Secret Rotation**: Rotate JWT_SECRET monthly (manual process)
- **Short Expiry**: 7-day expiry forces re-authentication
- **HTTPS Only**: Tokens only transmitted over TLS
- **httpOnly Cookies**: Prevents XSS token theft (production)

### 2. User Isolation
- **Database Level**: All queries filtered by user_id
- **Middleware Enforcement**: JWT middleware extracts user_id
- **Validation**: Path parameter user_id must match JWT user_id
- **Testing**: Security audit tests for cross-user access

### 3. Input Sanitization
- **Pydantic Validation**: All inputs validated before processing
- **SQLModel ORM**: Parameterized queries prevent SQL injection
- **React Escaping**: React automatically escapes user content

### 4. Rate Limiting (Future)
- **Implementation**: Add rate limiting middleware (10 req/min per user)
- **Benefit**: Prevent abuse, protect API costs
- **Status**: Not in Phase 3 scope

---

## Deployment Strategy

### Development Environment
- **Frontend**: `npm run dev` on http://localhost:3000
- **Backend**: `uv run uvicorn main:app --reload` on http://localhost:8000
- **Database**: Neon PostgreSQL (development branch)

### Production Environment (Future)
- **Frontend**: Vercel deployment (automatic from GitHub)
- **Backend**: Docker container on AWS ECS or Render
- **Database**: Neon PostgreSQL (production branch)
- **Monitoring**: Sentry for error tracking, Datadog for metrics

### CI/CD Pipeline (Future)
- **Tests**: Run pytest + Playwright on pull requests
- **Linting**: black, isort, mypy, ESLint
- **Deployment**: Auto-deploy main branch to staging, manual promotion to production

---

## Conclusion

All technology decisions have been researched and documented with clear rationale. The chosen stack aligns with:
- **Constitution Principles**: Stateless, test-first, security-focused
- **Performance Requirements**: <2s response time, 100 concurrent users
- **Hackathon Constraints**: Fast setup, minimal infrastructure, demo-ready

Next steps: Proceed to Phase 1 (Data Model + Contracts design).
