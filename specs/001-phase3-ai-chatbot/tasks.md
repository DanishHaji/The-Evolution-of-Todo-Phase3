# Implementation Tasks: AI-Powered Todo Chatbot - Phase 3

**Feature**: 001-phase3-ai-chatbot
**Branch**: `001-phase3-ai-chatbot`
**Date**: 2026-01-16
**Status**: Ready for Implementation

---

## Overview

This task breakdown follows the constitution's test-first, spec-driven approach. Each user story is independently testable and can be delivered incrementally. Tasks are organized by priority (Critical → High → Medium) with clear dependencies and parallel execution opportunities.

**Total Estimated Tasks**: 87 tasks
**MVP Scope**: Phase 3 (US1 - Basic Chatbot Interface) = 25 tasks
**Parallel Opportunities**: 42 tasks marked [P] can run in parallel

---

## Implementation Strategy

### Delivery Approach
- **MVP First**: Phase 3 (US1) delivers core chatbot functionality
- **Incremental**: Each phase is a complete, testable increment
- **Independent Stories**: US2-US4 can be developed independently after US1

### Testing Strategy (Constitution Principle III)
- **TDD Required**: Write tests BEFORE implementation
- **80% Coverage Minimum**: All code must meet coverage threshold
- **Test Types**: Unit tests for tools/models, integration tests for agent flows, E2E tests for NL scenarios

### Parallel Execution
- Tasks marked `[P]` can run in parallel (different files, no blocking dependencies)
- Tasks marked `[US#]` belong to specific user stories
- Setup and foundational tasks must complete before user stories

---

## Dependencies and Execution Order

### Story Completion Order
```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (US4) → Phase 7 (Polish)
                                              ↓
                                            MVP Ready
```

### Story Dependencies
- **US1** (Basic Chatbot): No dependencies (starts after foundational)
- **US2** (Conversation Persistence): Depends on US1 (agent infrastructure)
- **US3** (Intermediate Features): Depends on US1 (basic tools working)
- **US4** (Advanced Features/Bonus): Depends on US1, US3 (extension of existing features)

### Parallel Execution Examples

**Phase 1 (Setup)**: After T001-T003 complete, T004-T007 can run in parallel (4 parallel streams)

**Phase 2 (Foundational)**: After T008-T010 complete, T011-T017 can run in parallel (7 parallel streams)

**Phase 3 (US1)**: After T018-T020 complete, T021-T029 can run in parallel (9 parallel streams)

---

## Phase 1: Project Setup & Infrastructure

**Goal**: Initialize project structure, install dependencies, configure environment

**Duration**: ~2-3 hours
**Parallel Opportunities**: 4 tasks
**Blocking**: Must complete before Phase 2

### Setup Tasks

- [X] T001 Create backend project structure at `backend/` with subdirectories: `app/`, `tests/`, `.env.example`
- [X] T002 Create frontend project structure at `frontend/` with Next.js App Router: `app/`, `components/`, `lib/`, `tests/`
- [X] T003 Initialize git repository, create `.gitignore` for Python and Node.js, commit initial structure

### Dependency Installation (Parallel)

- [X] T004 [P] Install UV package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh` and verify with `uv --version`
- [X] T005 [P] Backend: Install core dependencies with UV in `backend/`: `uv add fastapi uvicorn[standard] sqlmodel psycopg2-binary pydantic python-dotenv`
- [X] T006 [P] Backend: Install AI dependencies in `backend/`: `uv add agents cohere`
- [X] T007 [P] Backend: Install dev dependencies in `backend/`: `uv add --dev pytest pytest-asyncio httpx black isort mypy`

### Environment Configuration

- [X] T008 Create Neon PostgreSQL database: sign up at neon.tech, create project "phase3-todo-chatbot", copy connection string
- [X] T009 Get Cohere API key: sign up at cohere.com, generate API key, save key (starts with `co_`)
- [X] T010 Configure backend environment: create `backend/.env` with DATABASE_URL, JWT_SECRET (openssl rand -hex 32), BETTER_AUTH_SECRET, COHERE_API_KEY
- [X] T011 [P] Configure frontend environment: create `frontend/.env.local` with NEXT_PUBLIC_API_URL=http://localhost:8000, NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
- [X] T012 [P] Frontend: Install dependencies in `frontend/`: `npm install` (from package.json with Next.js 16+, React 19+, OpenAI ChatKit, Better Auth, Radix UI, Tailwind CSS v4)

**Acceptance Criteria**:
- ✅ Project structure matches architecture in plan.md
- ✅ All dependencies installed without errors
- ✅ Environment variables configured (API keys, database URL, JWT secrets)
- ✅ `uv --version` returns UV version
- ✅ `npm --version` returns npm 9+

---

## Phase 2: Foundational Components (Blocking Prerequisites)

**Goal**: Implement core infrastructure required by all user stories (database models, authentication, base FastAPI app)

**Duration**: ~4-5 hours
**Parallel Opportunities**: 7 tasks
**Blocking**: Must complete before US1 implementation

### Database Models (SQLModel)

- [ ] T013 Create `backend/app/models.py` with SQLModel base class and database engine setup (create_engine with DATABASE_URL from env)
- [ ] T014 [P] Implement User model in `backend/app/models.py` (note: managed by Better Auth, we only reference via FK)
- [ ] T015 [P] Implement Task model in `backend/app/models.py` with all fields: id, user_id (FK), title, description, priority (low/medium/high), tags (JSON), due_date, status (bool), recurring, created_at, updated_at
- [ ] T016 [P] Implement Conversation model in `backend/app/models.py` with fields: id, user_id (FK), created_at, updated_at
- [ ] T017 [P] Implement Message model in `backend/app/models.py` with fields: id, conversation_id (FK), user_id (FK), role (user/assistant), content (TEXT), created_at

### Database Tests (TDD)

- [ ] T018 Create `backend/tests/conftest.py` with pytest fixtures: test_engine (SQLite in-memory), test_session, mock JWT tokens
- [ ] T019 Write unit tests in `backend/tests/test_models.py`: test Task validation (priority enum, title required), test foreign key constraints, test timestamps auto-set
- [ ] T020 Run tests and verify failures: `uv run pytest backend/tests/test_models.py -v` (expect failures - RED phase)

### Database Implementation

- [ ] T021 Run database migrations: create init_db() function in `backend/app/models.py` using SQLModel.metadata.create_all(engine)
- [ ] T022 Execute migrations: `uv run python -c "from app.models import init_db; init_db()"` and verify tables created in Neon dashboard
- [ ] T023 Run model tests again: `uv run pytest backend/tests/test_models.py -v` and verify all pass (GREEN phase)

### FastAPI Application Setup

- [ ] T024 Create `backend/app/main.py` with FastAPI app initialization, CORS middleware (allow http://localhost:3000), health check endpoint GET /health returning {"status": "healthy", "database": "connected"}
- [ ] T025 Create `backend/app/auth.py` with JWT middleware: verify_jwt() function that extracts user_id from Authorization Bearer token, validates with JWT_SECRET, raises HTTPException 401 if invalid
- [ ] T026 Write auth tests in `backend/tests/test_auth.py`: test valid JWT extraction, test invalid token (401), test missing token (401), test expired token (401)
- [ ] T027 Implement JWT middleware in `backend/app/auth.py`: create FastAPI Depends function for JWT verification, test with pytest

### Test Foundational Components

- [ ] T028 Start backend server: `uv run uvicorn app.main:app --reload --port 8000` and verify health endpoint returns 200 OK
- [ ] T029 Run all foundational tests: `uv run pytest backend/tests/ -v --cov=app --cov-report=term` and verify >80% coverage

**Acceptance Criteria**:
- ✅ All 4 database models (User, Task, Conversation, Message) created with proper fields and constraints
- ✅ Database tables exist in Neon PostgreSQL (verify via Neon dashboard)
- ✅ FastAPI app starts without errors on port 8000
- ✅ GET /health returns 200 {"status": "healthy"}
- ✅ JWT middleware validates tokens correctly (tests pass)
- ✅ Test coverage >80% for models and auth modules

---

## Phase 3: User Story 1 - Basic Chatbot Interface (MVP)

**User Story**: FR-001 (Critical) - Users interact with Todo system via natural language through chat interface

**Goal**: Implement core chatbot functionality with 6 MCP tools (add, delete, update, list, complete, search tasks)

**Duration**: ~8-10 hours
**Parallel Opportunities**: 18 tasks
**MVP Delivery**: After this phase, chatbot is functional for basic todo operations

### MCP Tools Implementation (Backend)

- [ ] T030 Create `backend/app/mcp_tools.py` with imports: agents.function_tool, sqlmodel Session, typing Optional/List
- [ ] T031 [P] [US1] Implement add_task tool in `backend/app/mcp_tools.py`: parameters (title, desc, priority, tags, due_date, recurring, session, user_id), returns task_id, validates priority enum, parses ISO date
- [ ] T032 [P] [US1] Implement delete_task tool in `backend/app/mcp_tools.py`: parameters (task_id, session, user_id), returns bool, verifies ownership (task.user_id == user_id), requires agent confirmation in docstring
- [ ] T033 [P] [US1] Implement update_task tool in `backend/app/mcp_tools.py`: parameters (task_id, title?, description?, priority?, tags?, due_date?, status?, recurring?, session, user_id), returns updated task dict, validates ownership
- [ ] T034 [P] [US1] Implement list_tasks tool in `backend/app/mcp_tools.py`: parameters (status?, priority?, tags?, due_before?, due_after?, limit=50, session, user_id), returns List[dict], filters by user_id, supports tag matching (ANY tag)
- [ ] T035 [P] [US1] Implement complete_task tool in `backend/app/mcp_tools.py`: parameters (task_id, session, user_id), returns new_status (bool), toggles task.status, updates updated_at timestamp
- [ ] T036 [P] [US1] Implement search_tasks tool in `backend/app/mcp_tools.py`: parameters (query, limit=20, session, user_id), returns List[dict], case-insensitive ILIKE search on title and description

### MCP Tools Tests (TDD)

- [ ] T037 [US1] Write tool tests in `backend/tests/test_tools.py`: test add_task creates task with user_id filtering, test delete_task verifies ownership (ValueError if different user), test update_task modifies fields correctly
- [ ] T038 [US1] Write more tool tests in `backend/tests/test_tools.py`: test list_tasks with status/priority filters, test complete_task toggles status, test search_tasks finds tasks by keyword
- [ ] T039 [US1] Run tool tests: `uv run pytest backend/tests/test_tools.py -v` and verify failures (RED phase - tools not yet integrated)

### OpenAI Agents SDK + Cohere Integration

- [ ] T040 [US1] Create `backend/app/agent.py` with Cohere client setup: AsyncOpenAI(api_key=COHERE_API_KEY, base_url="https://api.cohere.ai/v1")
- [ ] T041 [US1] Configure Cohere model in `backend/app/agent.py`: OpenAIChatCompletionsModel(model="command-r", openai_client=cohere_client)
- [ ] T042 [US1] Create TodoAgent in `backend/app/agent.py`: Agent(name="TodoAgent", instructions="Parse NL to call MCP tools. CONFIRM destructive actions. Filter by user_id automatic. Return natural language, not JSON.", tools=[all 6 tools])
- [ ] T043 [US1] Implement run_agent() function in `backend/app/agent.py`: accepts (query: str, user_id: int, db_session: Session), injects user_id and session into tools, runs Runner.run_sync(), returns final_output string

### Agent Tests

- [ ] T044 [US1] Write agent integration tests in `backend/tests/test_agent.py`: test agent calls add_task for "Add task to buy groceries", test agent calls list_tasks for "Show my tasks", test agent asks confirmation for "Delete all tasks"
- [ ] T045 [US1] Run agent tests: `uv run pytest backend/tests/test_agent.py -v` and verify failures (RED phase)

### Chat API Endpoint

- [ ] T046 [US1] Create `backend/app/chat.py` with ChatRequest Pydantic model: query (str), conversation_id (Optional[int])
- [ ] T047 [US1] Create `backend/app/chat.py` with ChatResponse Pydantic model: response (str), conversation_id (int), tasks (Optional[List[dict]]), metadata (Optional[dict])
- [ ] T048 [US1] Implement POST /api/{user_id}/chat endpoint in `backend/app/chat.py`: verify JWT user_id matches path user_id (403 if mismatch), create DB session, call run_agent(), return ChatResponse
- [ ] T049 [US1] Register chat router in `backend/app/main.py`: app.include_router(chat_router, prefix="/api", tags=["chat"])

### Chat API Tests

- [ ] T050 [US1] Write API tests in `backend/tests/test_api.py`: test POST /api/1/chat with valid JWT and query "Add task", test 401 with invalid JWT, test 403 with user_id mismatch, test 400 with empty query
- [ ] T051 [US1] Run API tests: `uv run pytest backend/tests/test_api.py -v` and verify all pass (GREEN phase)

### Frontend: Better Auth Setup

- [ ] T052 [US1] Create `frontend/lib/auth.ts` with Better Auth client: BetterAuth({baseURL: NEXT_PUBLIC_API_URL, credentials: {username: true, password: true}, jwt: {secret: BETTER_AUTH_SECRET, expiresIn: "7d"}})
- [ ] T053 [US1] Create `frontend/components/AuthProvider.tsx` with useAuth hook providing: user, token, login(), logout(), signup()
- [ ] T054 [US1] Update `frontend/app/layout.tsx` to wrap children with <AuthProvider>

### Frontend: ChatKit Integration

- [ ] T055 [US1] Create `frontend/components/ChatbotIcon.tsx`: floating button (Heroicons ChatBubbleLeftIcon) in bottom-right corner, onClick opens modal
- [ ] T056 [US1] Create `frontend/components/ChatbotModal.tsx`: OpenAI ChatKit component with props - apiUrl="/api/${userId}/chat", headers with Authorization Bearer token, onMessageSend calls API, displays messages with user/assistant roles
- [ ] T057 [US1] Implement handleSendMessage in `frontend/components/ChatbotModal.tsx`: fetch POST to chat API with JWT header, parse response, append to messages state, handle errors (display user-friendly message)
- [ ] T058 [US1] Add ChatbotIcon to `frontend/app/layout.tsx` after main content, only show when user authenticated

### E2E Tests (TDD)

- [ ] T059 [US1] Create `frontend/tests/e2e/chat.spec.ts` with Playwright: test user can add task via "Add task to buy groceries", test bot responds with confirmation, test task appears in database
- [ ] T060 [US1] Write more E2E tests in `frontend/tests/e2e/chat.spec.ts`: test user can list tasks via "Show my tasks", test user can delete task with confirmation, test user can search tasks by keyword
- [ ] T061 [US1] Run E2E tests: `npm run test:e2e` and verify failures (RED phase - frontend not integrated yet)

### Frontend Implementation & Testing

- [ ] T062 [US1] Start frontend dev server: `npm run dev` and verify http://localhost:3000 loads without errors
- [ ] T063 [US1] Manual test: Login with test user, click chat icon, send "Add task to buy groceries", verify bot responds and task created
- [ ] T064 [US1] Run E2E tests: `npm run test:e2e` and verify all pass (GREEN phase)

### Integration & Coverage

- [ ] T065 [US1] Run full backend test suite: `uv run pytest backend/tests/ -v --cov=app --cov-report=html` and verify >80% coverage
- [ ] T066 [US1] Review coverage report at `backend/htmlcov/index.html`, identify untested lines, add tests if coverage <80%
- [ ] T067 [US1] Run full frontend test suite: `npm test` and verify all unit tests pass

**Acceptance Criteria (US1)**:
- ✅ User can add tasks via NL: "Add task to buy groceries tomorrow"
- ✅ User can list tasks via NL: "Show my high priority tasks"
- ✅ User can delete tasks with confirmation: "Delete task 123" → bot confirms before deleting
- ✅ User can update tasks: "Change task 123 priority to high"
- ✅ User can mark tasks complete: "Mark task 123 as complete"
- ✅ User can search tasks: "Find tasks about groceries"
- ✅ Bot responds in natural language (no raw JSON)
- ✅ Chat interface embedded in Next.js UI via floating icon
- ✅ All operations filtered by user_id (no cross-user access)
- ✅ Test coverage >80% for backend (models, tools, agent, API)
- ✅ E2E tests pass for all 6 MCP tool operations

**MVP Delivery**: ✅ After T067, chatbot is functional for basic todo management

---

## Phase 4: User Story 2 - Conversation Persistence (Stateless Architecture)

**User Story**: FR-004 (Critical) - All conversations persist to database for stateless architecture

**Goal**: Store conversation history in Conversation/Message tables, enable conversation resumption on page reload

**Duration**: ~3-4 hours
**Parallel Opportunities**: 5 tasks
**Dependencies**: Requires US1 (agent infrastructure working)

### Conversation Persistence Backend

- [ ] T068 [US2] Update `backend/app/chat.py` to create or load Conversation: on first request from user, create new Conversation(user_id), on subsequent requests use conversation_id from request, update conversation.updated_at on each message
- [ ] T069 [P] [US2] Implement save_message() helper in `backend/app/chat.py`: accepts (conversation_id, user_id, role, content, session), creates Message record, commits to database
- [ ] T070 [P] [US2] Implement load_conversation_history() helper in `backend/app/chat.py`: accepts (conversation_id, limit=50, session), queries Message.where(conversation_id).order_by(created_at DESC).limit(limit), returns list of messages (oldest first)
- [ ] T071 [US2] Update run_agent() in `backend/app/agent.py` to accept conversation_history parameter, prepend history to agent context before running
- [ ] T072 [US2] Update POST /api/{user_id}/chat in `backend/app/chat.py`: load conversation history, save user message before agent run, run agent with history context, save assistant response after agent run, return conversation_id in response

### Conversation Tests

- [ ] T073 [US2] Write conversation tests in `backend/tests/test_conversation.py`: test save_message creates Message record, test load_conversation_history returns messages in order, test conversation_id returned in ChatResponse
- [ ] T074 [US2] Write integration test in `backend/tests/test_conversation.py`: test multi-turn conversation (send 3 messages, verify history persists, verify agent context includes history)
- [ ] T075 [US2] Run conversation tests: `uv run pytest backend/tests/test_conversation.py -v` and verify all pass

### Frontend: Conversation Resumption

- [ ] T076 [P] [US2] Update `frontend/components/ChatbotModal.tsx` to load conversation history on mount: fetch GET /api/{user_id}/conversations (new endpoint), display last 50 messages
- [ ] T077 [P] [US2] Update `frontend/components/ChatbotModal.tsx` to include conversation_id in chat requests: store conversation_id in state after first message, send in subsequent requests
- [ ] T078 [US2] Implement GET /api/{user_id}/conversations endpoint in `backend/app/chat.py`: returns user's conversations ordered by updated_at DESC, includes message count per conversation
- [ ] T079 [US2] Update frontend handleSendMessage to persist conversation_id in localStorage for resumption after page reload

### E2E Tests

- [ ] T080 [US2] Write E2E test in `frontend/tests/e2e/conversation.spec.ts`: test conversation persists across page reloads (send message, reload page, verify message history loaded)
- [ ] T081 [US2] Write E2E test in `frontend/tests/e2e/conversation.spec.ts`: test multi-turn conversation (send 3 messages, verify agent responds with context from previous messages)
- [ ] T082 [US2] Run E2E tests: `npm run test:e2e` and verify conversation tests pass

**Acceptance Criteria (US2)**:
- ✅ All user and assistant messages stored in Message table
- ✅ Conversation history loaded on chat modal open (last 50 messages)
- ✅ Agent receives conversation history as context (multi-turn conversations work)
- ✅ Conversation resumes after page reload (conversation_id persisted)
- ✅ User can see all their conversations (GET /api/{user_id}/conversations)
- ✅ E2E tests verify conversation persistence across page reloads
- ✅ Stateless architecture: no server-side sessions, all state in database

---

## Phase 5: User Story 3 - Intermediate Features

**User Story**: FR-002 (High) - Support advanced task management via natural language

**Goal**: Implement recurring tasks, bulk operations, tag-based filtering, NL date parsing

**Duration**: ~4-5 hours
**Parallel Opportunities**: 8 tasks
**Dependencies**: Requires US1 (basic tools working)

### Recurring Tasks

- [ ] T083 [P] [US3] Update add_task tool in `backend/app/mcp_tools.py` to support recurring parameter validation (daily/weekly/monthly/yearly)
- [ ] T084 [P] [US3] Update list_tasks tool in `backend/app/mcp_tools.py` to filter by recurring field
- [ ] T085 [P] [US3] Write tests in `backend/tests/test_recurring.py`: test create recurring task "Review emails every weekday at 9 AM", test list recurring tasks, test update recurring pattern

### Bulk Operations

- [ ] T086 [P] [US3] Implement bulk_update_tasks tool in `backend/app/mcp_tools.py`: parameters (filter: dict, updates: dict, session, user_id), returns count of updated tasks, validates user_id on all filtered tasks
- [ ] T087 [P] [US3] Implement bulk_delete_tasks tool in `backend/app/mcp_tools.py`: parameters (filter: dict, session, user_id), returns count of deleted tasks, requires agent confirmation in docstring
- [ ] T088 [US3] Add bulk tools to agent in `backend/app/agent.py`, update agent instructions to confirm bulk operations with count (e.g., "You have 5 completed tasks. Delete all? (yes/no)")
- [ ] T089 [US3] Write bulk operation tests in `backend/tests/test_bulk.py`: test "Mark all overdue tasks as high priority", test "Delete all completed tasks" with confirmation

### Natural Language Date Parsing

- [ ] T090 [P] [US3] Install dateparser library: `uv add dateparser` in backend/
- [ ] T091 [P] [US3] Implement parse_nl_date() helper in `backend/app/mcp_tools.py`: uses dateparser.parse() to convert "tomorrow", "next Friday", "in 2 hours" to datetime, handles timezone
- [ ] T092 [US3] Update add_task and update_task tools to use parse_nl_date() for due_date parameter
- [ ] T093 [US3] Write NL date tests in `backend/tests/test_nl_date.py`: test "tomorrow" parsing, test "next Friday" parsing, test "in 2 hours" relative time, test invalid dates return None

### Tag-Based Operations

- [ ] T094 [P] [US3] Update list_tasks tool to support tag filtering with OR logic (match ANY tag in list)
- [ ] T095 [P] [US3] Implement get_tags tool in `backend/app/mcp_tools.py`: returns all unique tags used by user (for autocomplete), parameters (session, user_id), returns List[str]
- [ ] T096 [US3] Write tag tests in `backend/tests/test_tags.py`: test list tasks by tags ["work", "urgent"], test get_tags returns unique tags

### Integration & E2E Tests

- [ ] T097 [US3] Write E2E test in `frontend/tests/e2e/intermediate.spec.ts`: test create recurring task via NL, test bulk delete with confirmation, test NL date parsing ("Add task due tomorrow")
- [ ] T098 [US3] Run all US3 tests: `uv run pytest backend/tests/test_recurring.py backend/tests/test_bulk.py backend/tests/test_nl_date.py backend/tests/test_tags.py -v` and verify all pass
- [ ] T099 [US3] Run E2E tests: `npm run test:e2e frontend/tests/e2e/intermediate.spec.ts` and verify all pass

**Acceptance Criteria (US3)**:
- ✅ User can create recurring tasks: "Review emails every weekday at 9 AM"
- ✅ User can perform bulk operations: "Mark all overdue tasks as high priority"
- ✅ Bot confirms bulk operations with count before execution
- ✅ User can filter tasks by tags: "Show tasks tagged work and urgent"
- ✅ Natural language date parsing works: "tomorrow", "next Friday", "in 2 hours"
- ✅ Tests pass for recurring tasks, bulk operations, NL dates, tags

---

## Phase 6: User Story 4 - Advanced Features (Bonus)

**User Story**: FR-003 (Medium) - Enhanced capabilities for power users (multi-language, voice commands)

**Goal**: Implement Urdu support via Cohere multilingual, voice input via browser SpeechRecognition API

**Duration**: ~3-4 hours
**Parallel Opportunities**: 5 tasks
**Dependencies**: Requires US1, US3 (extension of existing features)

### Multi-Language Support (Urdu)

- [ ] T100 [P] [US4] Update agent instructions in `backend/app/agent.py` to support Urdu: "You can respond in Urdu or English based on user's language. Cohere command-r supports multilingual."
- [ ] T101 [P] [US4] Test Cohere multilingual: send Urdu NL query "کام شامل کریں" (Add task) and verify agent responds in Urdu with correct task creation
- [ ] T102 [US4] Write multilingual tests in `backend/tests/test_multilingual.py`: test Urdu query creates task, test agent responds in Urdu, test mixed English/Urdu conversation

### Voice Commands (Frontend)

- [ ] T103 [P] [US4] Implement voice input in `frontend/components/ChatbotModal.tsx`: add microphone button using Heroicons MicrophoneIcon, use browser SpeechRecognition API to capture voice, convert speech to text, send as query
- [ ] T104 [P] [US4] Add voice input error handling in `frontend/components/ChatbotModal.tsx`: check if SpeechRecognition supported in browser, display message if not supported (graceful degradation), handle recognition errors
- [ ] T105 [US4] Write voice input tests in `frontend/tests/unit/voice.test.ts`: test microphone button appears, test SpeechRecognition API called on button click (mock API)

### E2E Tests

- [ ] T106 [US4] Write E2E test in `frontend/tests/e2e/advanced.spec.ts`: test Urdu query via text input (skip voice due to browser automation limitations), verify task created and bot responds in Urdu
- [ ] T107 [US4] Run all US4 tests: `uv run pytest backend/tests/test_multilingual.py -v` and `npm test frontend/tests/unit/voice.test.ts` and verify all pass

**Acceptance Criteria (US4)**:
- ✅ User can send Urdu queries and bot responds in Urdu
- ✅ Voice input button appears in chat modal (microphone icon)
- ✅ Voice commands convert to text and send as query (on supported browsers)
- ✅ Graceful degradation: voice input hidden if browser doesn't support SpeechRecognition
- ✅ Tests pass for multilingual support and voice input

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize documentation, optimize performance, ensure production readiness

**Duration**: ~2-3 hours
**Parallel Opportunities**: 6 tasks

### Performance Optimization

- [ ] T108 [P] Implement database connection pooling in `backend/app/models.py`: configure engine with pool_size=10, max_overflow=20, pool_pre_ping=True
- [ ] T109 [P] Add query optimization: create indexes on Task(user_id, status), Task(user_id, priority), Message(conversation_id, created_at) using Alembic or SQLModel
- [ ] T110 [P] Implement conversation history pruning in `backend/app/chat.py`: limit to 50 messages, archive older messages (future enhancement placeholder)

### Security Hardening

- [ ] T111 [P] Add rate limiting middleware in `backend/app/main.py`: 10 requests/minute per user (use slowapi library: `uv add slowapi`)
- [ ] T112 [P] Update CORS configuration in `backend/app/main.py`: restrict to production frontend URL (not wildcard), allow credentials
- [ ] T113 Implement input sanitization in `backend/app/mcp_tools.py`: validate title/description length limits, strip HTML tags, prevent XSS

### Documentation

- [ ] T114 [P] Create `backend/README.md` with setup instructions, API endpoints, testing commands
- [ ] T115 [P] Create `frontend/README.md` with setup instructions, component structure, testing commands
- [ ] T116 Update root `README.md` with Phase 3 overview, architecture diagram (text-based), quickstart link

### Final Testing

- [ ] T117 Run full backend test suite with coverage: `uv run pytest backend/tests/ -v --cov=app --cov-report=html --cov-fail-under=80` and verify >80% coverage
- [ ] T118 Run full frontend test suite: `npm test && npm run test:e2e` and verify all tests pass
- [ ] T119 Manual smoke test: start both services, test end-to-end flow (signup, login, add task via chat, list tasks, delete task, logout)

**Acceptance Criteria (Polish)**:
- ✅ Database connection pooling configured
- ✅ Query performance optimized with indexes
- ✅ Rate limiting prevents abuse (10 req/min per user)
- ✅ CORS restricted to production domain
- ✅ Input sanitization prevents XSS
- ✅ Documentation complete (backend README, frontend README, root README)
- ✅ Test coverage >80% for all modules
- ✅ All tests passing (unit, integration, E2E)
- ✅ Manual smoke test passes

---

## Deployment Checklist (Post-Implementation)

These tasks are for production deployment (not part of implementation phases):

- [ ] D001 Set up Vercel project for frontend deployment
- [ ] D002 Set up Render/AWS ECS for backend deployment
- [ ] D003 Configure production environment variables (DATABASE_URL, COHERE_API_KEY, JWT_SECRET)
- [ ] D004 Run database migrations on production Neon database
- [ ] D005 Set up Sentry for error tracking (backend and frontend)
- [ ] D006 Configure CI/CD pipeline (GitHub Actions): run tests on PR, auto-deploy on merge to main
- [ ] D007 Set up monitoring with Datadog (track API latency, error rates, Cohere API usage)
- [ ] D008 Create Kubernetes manifests (optional): Deployment, Service, Ingress for backend
- [ ] D009 Perform load testing with 100 concurrent users (verify <2s response time requirement)
- [ ] D010 Security audit: test cross-user access prevention, JWT token security, input sanitization

---

## Task Summary

### Total Task Count: 119 tasks
- **Phase 1 (Setup)**: 12 tasks (4 parallel)
- **Phase 2 (Foundational)**: 17 tasks (7 parallel)
- **Phase 3 (US1 - MVP)**: 38 tasks (18 parallel)
- **Phase 4 (US2)**: 15 tasks (5 parallel)
- **Phase 5 (US3)**: 17 tasks (8 parallel)
- **Phase 6 (US4)**: 8 tasks (5 parallel)
- **Phase 7 (Polish)**: 12 tasks (6 parallel)
- **Deployment**: 10 tasks (post-implementation)

### Parallel Execution Opportunities: 53 tasks marked [P]

### MVP Scope (Minimum Viable Product)
**Phase 1 + Phase 2 + Phase 3 = 67 tasks**

After completing Phase 3 (T001-T067), the chatbot is functional for basic todo management with:
- ✅ 6 MCP tools (add, delete, update, list, complete, search)
- ✅ Natural language interface via ChatKit
- ✅ JWT authentication with user isolation
- ✅ Database persistence with SQLModel + Neon PostgreSQL
- ✅ OpenAI Agents SDK + Cohere API for NL processing
- ✅ Test coverage >80%

### Test Coverage Breakdown
- **Unit Tests**: 30 tasks (models, tools, auth, agent)
- **Integration Tests**: 10 tasks (API endpoints, agent flows)
- **E2E Tests**: 8 tasks (chat interactions, conversation persistence, advanced features)
- **Total Test Tasks**: 48 tasks (~40% of implementation tasks are tests)

### Estimated Timeline
- **MVP (Phase 1-3)**: 14-18 hours
- **Full Implementation (Phase 1-7)**: 24-30 hours
- **With Deployment**: 28-34 hours

---

## Success Metrics (Phase 3 Constitution Compliance)

### Stateless Architecture (Principle I)
- ✅ All conversation state in database (Conversation/Message tables)
- ✅ No server-side sessions (JWT tokens only)
- ✅ MCP tools receive DB session as parameter (no global state)

### Test-First Development (Principle III)
- ✅ 80% code coverage minimum achieved
- ✅ Tests written BEFORE implementation (TDD RED-GREEN cycle followed)
- ✅ Unit + Integration + E2E tests for all features

### Security & User Isolation (Principle V)
- ✅ JWT authentication on all endpoints (except /health)
- ✅ user_id filtering on all database queries
- ✅ Cross-user access prevention tested

### Database-First Persistence (Principle VI)
- ✅ SQLModel ORM for type-safe operations
- ✅ All state persisted to Neon PostgreSQL
- ✅ Foreign key constraints enforce data integrity

---

## Notes for Implementation

1. **TDD Approach**: Follow RED-GREEN-REFACTOR cycle strictly (constitution requirement)
   - Write test (RED) → Implement feature (GREEN) → Refactor if needed

2. **Parallel Execution**: Tasks marked [P] can run in parallel to speed up development
   - Example: All 6 MCP tools (T031-T036) can be implemented simultaneously by different developers

3. **User Story Independence**: US2, US3, US4 can be developed independently after US1 completes
   - Teams can work on multiple stories in parallel after foundational phase

4. **MVP Strategy**: Focus on Phase 1-3 first (67 tasks) for rapid demo
   - Delivers core chatbot functionality in ~14-18 hours

5. **Error Handling**: All API endpoints must return user-friendly error messages (not stack traces)
   - Use Pydantic ValidationError for 400 responses
   - Use HTTPException for 401/403/404/500 responses

6. **Code Quality**: Run black + isort + mypy before committing (constitution requirement)
   - `uv run black . && uv run isort . && uv run mypy app/`

7. **Commit Messages**: Use conventional commits format
   - Example: `feat(tools): implement add_task MCP tool with user_id filtering`
   - Example: `test(agent): add integration tests for agent tool calling`

---

**Next Steps**: Run `/sp.implement` to begin task execution with TDD approach
