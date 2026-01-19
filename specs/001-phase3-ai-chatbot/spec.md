# Specification: AI-Powered Todo Chatbot - Phase 3

**Feature ID**: 001-phase3-ai-chatbot
**Date**: 2026-01-16
**Status**: Planning
**Author**: User (via /sp.specify)

## Overview

This specification defines Phase 3 of the "Evolution of Todo" project for Hackathon II. The goal is to extend the Phase 2 full-stack web application into an AI-powered conversational chatbot capable of managing Todo lists via natural language (NL) inputs.

### Key Objectives

- Enable natural language interactions for all Todo operations (e.g., "Add task to buy groceries", "Reschedule meetings to 2 PM")
- Ensure stateless operations with Neon DB persistence for conversation history
- Integrate Cohere API (instead of Gemini) for enhanced NL processing via OpenAI Agents SDK
- Use UV package manager for backend dependencies to simplify setup
- Embed chatbot interface in Next.js UI via OpenAI ChatKit
- Prepare for bonus features: reusable intelligence, multi-language support

### Technology Stack

- **Frontend**: Next.js 16+ App Router, OpenAI ChatKit, Better Auth (JWT)
- **Backend**: FastAPI, OpenAI Agents SDK (adapted for Cohere API), Official MCP SDK
- **Database**: Neon PostgreSQL with SQLModel ORM
- **AI Model**: Cohere API (command-r model) for natural language understanding
- **Package Manager**: UV (Python), npm (Node.js)

## Functional Requirements

### FR-001: Chatbot Interface

**Priority**: Critical
**Description**: Users must interact with the Todo system via natural language through a chat interface

**Acceptance Criteria**:
- Support all Basic Todo features via NL commands:
  - Add tasks with title, description, priority, tags, due date
  - Update existing tasks (modify any field)
  - Delete tasks with confirmation dialog
  - Mark tasks as complete/incomplete
  - List tasks with filters (status, priority, date range, tags)
  - Search tasks by keywords
- Confirm destructive actions (deletes, bulk operations) before execution
- Resume conversations from database history on page reload
- Handle ambiguous queries by asking clarifying questions
- Display user-friendly error messages for invalid inputs

**Examples**:
```
User: "Add task to buy groceries tomorrow"
Bot: "I've added 'Buy groceries' to your tasks, due tomorrow at 12:00 PM. Would you like to set a priority?"

User: "Delete all completed tasks"
Bot: "You have 5 completed tasks. Are you sure you want to delete them all? (yes/no)"

User: "Show my high priority tasks"
Bot: "Here are your 3 high priority tasks: [list with details]"
```

### FR-002: Intermediate Features

**Priority**: High
**Description**: Support advanced task management via natural language

**Acceptance Criteria**:
- Recurring tasks (daily, weekly, monthly patterns)
- Subtask management with parent-child relationships
- Bulk operations (e.g., "Mark all overdue tasks as high priority")
- Tag-based organization and filtering
- Due date parsing from natural language (e.g., "next Friday", "in 2 hours")

**Examples**:
```
User: "Create a recurring task to review emails every weekday at 9 AM"
Bot: "Created recurring task 'Review emails' scheduled for weekdays at 9:00 AM"

User: "Add subtasks to 'Plan vacation': research destinations, book flights, reserve hotel"
Bot: "Added 3 subtasks to 'Plan vacation' task"
```

### FR-003: Advanced Features (Bonus)

**Priority**: Medium
**Description**: Enhanced capabilities for power users

**Acceptance Criteria**:
- Multi-language support (Urdu via Cohere multilingual)
- Voice command input (browser SpeechRecognition API)
- Smart suggestions based on task history
- Natural language date/time extraction
- Task dependencies and auto-scheduling

### FR-004: Conversation Persistence

**Priority**: Critical
**Description**: All conversations must persist to database for stateless architecture

**Acceptance Criteria**:
- Store all messages (user + assistant) in Conversation/Message tables
- Associate conversations with authenticated user_id
- Load last 50 messages on chat window open
- Prune older messages to maintain performance
- Support multiple concurrent conversations per user

## Non-Functional Requirements

### NFR-001: Performance

- Chat API response time: <2 seconds for NL query processing
- Database queries: <500ms for CRUD operations
- Agent tool calls: <1 second per MCP tool invocation
- Support 100 concurrent users without degradation

### NFR-002: Security

- JWT authentication mandatory for all API endpoints (except /health)
- User ID extracted from JWT claims; never trust client input
- All database queries MUST filter by user_id (no cross-user data leakage)
- Input sanitization for XSS and SQL injection prevention
- Secrets stored in environment variables only
- HTTPS required for production deployment

### NFR-003: Scalability

- Stateless design for horizontal scaling
- Kubernetes-ready (no in-memory session state)
- Database connection pooling (max 20 connections per instance)
- Agent context window: 8K tokens (Cohere command-r limit)
- Max 1000 tasks per user

### NFR-004: Compatibility

- Cross-browser support (Chrome, Firefox, Safari, Edge)
- Mobile-responsive UI for chat interface
- Graceful degradation for voice commands on unsupported browsers

### NFR-005: Accessibility

- WCAG 2.1 Level AA compliant
- ARIA labels for chat interface components
- Keyboard navigation support
- Screen reader compatibility

### NFR-006: Testing

- Minimum 80% code coverage for all components
- Unit tests for all MCP tools and API endpoints
- Integration tests for Agent + MCP tool flows
- E2E tests for natural language scenarios
- Edge case tests (invalid JWT, ambiguous NL, DB failures)

## Architecture

### High-Level Flow

```
User → Next.js UI (Chat Icon → ChatKit Modal)
  ↓ (JWT in Authorization header)
FastAPI Backend (/api/{user_id}/chat)
  ↓ (Verify JWT, extract user_id)
OpenAI Agents SDK Runner (Cohere API)
  ↓ (NL parsing → tool selection)
MCP Tools (Stateless DB operations via SQLModel)
  ↓ (Filter by user_id)
Neon PostgreSQL Database
  ↓ (Persist tasks, conversations, messages)
Response → User (via ChatKit)
```

### Component Architecture

**Frontend Components**:
- `ChatbotIcon`: Floating button or navbar icon (Heroicons chat bubble)
- `ChatKitModal`: OpenAI ChatKit integration with JWT header injection
- `AuthProvider`: Better Auth context for JWT token management
- `ApiClient`: HTTP client with Bearer token auto-injection

**Backend Components**:
- `FastAPI Application`: Main server with CORS, JWT middleware
- `JWTMiddleware`: Token verification and user_id extraction
- `ChatRouter`: Endpoint handlers for /api/{user_id}/chat
- `AgentRunner`: OpenAI Agents SDK runner with Cohere client
- `MCPTools`: Stateless tool functions decorated with @function_tool
- `DatabaseSession`: SQLModel session management with connection pooling

**Database Models** (SQLModel):
- `User`: Managed by Better Auth (id, email, password_hash, created_at)
- `Task`: Todo task model (id, user_id, title, description, priority, tags, due_date, status, recurring, created_at, updated_at)
- `Conversation`: Chat conversation (id, user_id, created_at, updated_at)
- `Message`: Chat message (id, conversation_id, user_id, role, content, created_at)

### MCP Tools Specification

**Tool Definitions** (stateless, DB session passed from FastAPI):

1. **add_task**(title: str, desc: str, priority: str, tags: list, due_date: str, user_id: int, session: Session) -> int
   - Creates new task in database filtered by user_id
   - Returns task ID for confirmation message

2. **delete_task**(id: int, user_id: int, session: Session) -> bool
   - Deletes task after confirmation
   - Returns success/failure status

3. **update_task**(id: int, user_id: int, session: Session, **kwargs) -> Task
   - Updates task fields (title, description, priority, tags, due_date, status)
   - Returns updated task object

4. **list_tasks**(filter: dict, user_id: int, session: Session) -> List[Task]
   - Retrieves tasks with filters (status, priority, date_range, tags)
   - Returns list of Task objects

5. **complete_task**(id: int, user_id: int, session: Session) -> bool
   - Toggles task completion status
   - Returns new status

6. **search_tasks**(query: str, user_id: int, session: Session) -> List[Task]
   - Keyword search across title and description
   - Returns matching tasks

### API Endpoints

**POST /api/{user_id}/chat**
- **Headers**: `Authorization: Bearer <JWT>`
- **Request Body**: `{"query": str, "conversation_id": int (optional)}`
- **Response**: `{"response": str, "tasks": List[Task], "conversation_id": int}`
- **Authentication**: JWT verified, user_id extracted and matched against path parameter
- **Process**:
  1. Verify JWT and extract user_id
  2. Validate user_id matches path parameter
  3. Fetch conversation history from database
  4. Run OpenAI Agents SDK with Cohere API
  5. Invoke appropriate MCP tools with user_id filtering
  6. Persist message exchange to database
  7. Return user-friendly response

**GET /health**
- **Response**: `{"status": "healthy", "database": "connected"}`
- **No authentication required**

### Authentication Flow

1. **Frontend Login** (Better Auth):
   - User submits email/password
   - Better Auth generates JWT token (7-day expiry)
   - Token stored in httpOnly cookie (production) or localStorage (dev)

2. **API Request**:
   - Frontend ApiClient attaches JWT in `Authorization: Bearer <token>` header
   - FastAPI JWT middleware verifies signature and expiry
   - Middleware extracts user_id from JWT claims (sub field)
   - Request context populated with authenticated user_id

3. **Database Query**:
   - All MCP tools receive user_id parameter
   - SQLModel queries automatically filter by user_id
   - Prevents cross-user data access

### Database Schema

**Task Table**:
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: str = Field(default="")
    priority: str = Field(default="medium")  # low/medium/high
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    due_date: Optional[datetime] = Field(default=None)
    status: bool = Field(default=False)  # False=incomplete, True=complete
    recurring: Optional[str] = Field(default=None)  # e.g., "weekly", "daily"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Conversation Table**:
```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Message Table**:
```python
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str = Field(sa_column=Column(TEXT))
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Indexes**:
- `task.user_id` - Fast filtering by user
- `task.created_at` - Date range queries
- `message.conversation_id` - Load conversation history
- `message.user_id` - User isolation

## Dependencies

### Backend (Python - UV)
```bash
uv add fastapi uvicorn sqlmodel psycopg2-binary pydantic python-dotenv
uv add agents cohere  # OpenAI Agents SDK + Cohere API
uv add pytest pytest-asyncio httpx  # Testing
```

### Frontend (TypeScript - npm)
```bash
npm install next@latest react@latest react-dom@latest
npm install @openai/chatkit better-auth
npm install @radix-ui/react-* tailwindcss postcss autoprefixer
npm install zod react-hook-form @hookform/resolvers
```

## Configuration

### Environment Variables (.env)

```bash
# Backend
DATABASE_URL=postgresql://user:password@host:5432/database
JWT_SECRET=your-super-secret-jwt-key-change-in-production
BETTER_AUTH_SECRET=your-better-auth-secret-key
COHERE_API_KEY=your-cohere-api-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Testing Strategy

### Unit Tests (pytest)
- Test each MCP tool function with mock database session
- Test JWT middleware with valid/invalid/expired tokens
- Test Pydantic models for validation rules

### Integration Tests
- Test Agent + MCP tool flow end-to-end
- Test database transactions (rollback on errors)
- Test conversation history persistence

### E2E Tests (Playwright)
- Natural language scenarios:
  - "Add task to buy groceries" → Verify task created
  - "Delete task 123" → Confirm dialog → Verify deletion
  - "Show my high priority tasks" → Verify filtered list
- Edge cases:
  - Invalid JWT → 401 response
  - Ambiguous NL → Agent asks clarifying question
  - Database failure → User-friendly error message

## Acceptance Criteria

### Phase 3 Success Criteria
- [ ] User can add/update/delete/list tasks via natural language
- [ ] Chat interface embedded in Next.js UI via ChatKit
- [ ] All conversations persist to database and resume on reload
- [ ] JWT authentication enforces user isolation
- [ ] Response time <2s for NL processing
- [ ] 80% code coverage with passing tests
- [ ] No cross-user data leakage (security audit)
- [ ] Deployed to cloud with stateless architecture

### Bonus Criteria
- [ ] Multi-language support (Urdu) functional
- [ ] Voice commands working on supported browsers
- [ ] Smart task suggestions based on history
- [ ] Kubernetes deployment manifests ready

## Out of Scope

- Phase 2 basic web UI (assumed prerequisite but not implemented)
- Mobile native apps (iOS/Android)
- Real-time collaboration between users
- Email/SMS notifications for task reminders
- File attachments to tasks
- Calendar integration (Google Calendar, Outlook)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Cohere API rate limits hit | High | Implement request queuing and user feedback |
| Agent misinterprets NL commands | Medium | Add explicit confirmation for destructive actions |
| Database connection pool exhaustion | High | Configure max connections, add connection timeout handling |
| JWT secret compromise | Critical | Rotate secrets regularly, use short expiry |
| Cross-user data leakage | Critical | Enforce user_id filtering at ORM level, security audit |

## References

- OpenAI Agents SDK: https://github.com/openai/swarm (adapted for Cohere)
- Official MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Cohere API Docs: https://docs.cohere.com/
- OpenAI ChatKit: https://platform.openai.com/docs/chatkit
- Better Auth: https://www.better-auth.com/docs
- SQLModel Docs: https://sqlmodel.tiangolo.com/
- FastAPI Docs: https://fastapi.tiangolo.com/
