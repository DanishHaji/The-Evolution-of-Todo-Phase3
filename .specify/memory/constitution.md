# Phase 3 AI Todo Chatbot Constitution

## Core Principles

### I. Stateless Architecture (NON-NEGOTIABLE)
- All components must be stateless by design for cloud-native deployment
- Conversation state persists to Neon PostgreSQL, never in-memory
- No server-side sessions; JWT tokens for authentication
- MCP tools operate without internal state; DB session passed from caller
- Enables horizontal scaling and Kubernetes readiness
- **Rationale**: Ensures system can handle 100+ concurrent users and survive pod restarts

### II. Spec-Driven Development (SDD)
- All features must have specifications before implementation
- Use Spec-Kit Plus workflow: `/sp.specify` → `/sp.plan` → `/sp.tasks` → `/sp.implement`
- Architectural decisions documented via `/sp.adr` with user consent
- Prompt History Records (PHRs) created for all significant work
- Code generation via Claude Code only; no manual coding
- **Rationale**: Maintains traceability, enables team collaboration, enforces design-first approach

### III. Test-First Development (NON-NEGOTIABLE)
- Minimum 80% code coverage for all components
- Tests written and approved BEFORE implementation (Red-Green-Refactor)
- Required test types:
  - **Unit Tests**: All MCP tools, API endpoints, database models
  - **Integration Tests**: Agent + MCP tool flows, database transactions
  - **E2E Tests**: Natural language scenarios (e.g., "Add task to buy groceries")
  - **Edge Case Tests**: Invalid JWT, ambiguous NL, DB failures
- Use pytest for backend, Jest/Playwright for frontend
- **Rationale**: Ensures reliability for production deployment and catches regressions early

### IV. AI-First Development
- Natural language processing is the primary user interface
- OpenAI Agents SDK with Cohere API for enhanced NL understanding
- Agent must confirm destructive actions (deletes, bulk updates)
- Graceful handling of ambiguous queries (ask clarifying questions)
- Tool selection must be deterministic and logged for debugging
- **Rationale**: Delivers hackathon requirement of conversational Todo management

### V. Security & User Isolation
- JWT authentication mandatory for all API endpoints (except health checks)
- User ID extracted from verified JWT; never trust client input
- All database queries MUST filter by user_id (no cross-user data leakage)
- Input sanitization for XSS, SQL injection prevention
- Secrets stored in environment variables, never in code
- HTTPS required for production; secure cookie flags enabled
- **Rationale**: Protects user data privacy and prevents unauthorized access

### VI. Database-First Persistence
- SQLModel ORM for type-safe database operations
- All conversations, messages, and tasks persist to Neon PostgreSQL
- Schema migrations managed via Alembic (or SQLModel auto-migrations)
- Foreign key constraints enforced at database level
- Timestamps (created_at, updated_at) on all tables
- JSON columns for structured data (tags, conversation history)
- **Rationale**: Ensures data integrity and enables conversation resumption across sessions

### VII. API Contract Standards
- RESTful design for all endpoints
- Consistent error responses:
  - 200: Success with data
  - 400: Bad request (validation errors)
  - 401: Unauthorized (invalid/missing JWT)
  - 404: Resource not found
  - 500: Internal server error
- Request/response schemas validated via Pydantic
- API versioning via URL path (e.g., `/api/v1/...`)
- OpenAPI documentation auto-generated from FastAPI
- **Rationale**: Provides clear contracts for frontend-backend integration

## Technology Stack Standards

### Backend (Python)
- **Framework**: FastAPI 0.109+ for async support
- **ORM**: SQLModel for type-safe database operations
- **AI**: OpenAI Agents SDK + Cohere API (command-r model)
- **Tools**: Official MCP SDK for stateless tool definitions
- **Package Manager**: UV for fast dependency resolution
- **Testing**: pytest, pytest-asyncio, httpx for API tests
- **Database Driver**: psycopg2-binary for PostgreSQL

### Frontend (TypeScript)
- **Framework**: Next.js 16+ with App Router
- **UI Library**: OpenAI ChatKit for chat interface
- **Component Library**: Radix UI + Tailwind CSS v4
- **Auth**: Better Auth for JWT generation and management
- **HTTP Client**: Custom ApiClient with Bearer token injection
- **Testing**: Jest + Playwright for E2E tests

### Database
- **Provider**: Neon Serverless PostgreSQL
- **Schema**: User isolation via user_id foreign keys
- **Backups**: Automated daily backups (Neon managed)

### Infrastructure
- **Environment**: Development (localhost), Production (cloud-ready)
- **Configuration**: .env files for secrets (never committed to git)
- **Deployment**: Docker-ready (Dockerfile provided), Kubernetes manifests for bonuses

## Code Quality Standards

### Python (Backend)
- **Style**: PEP 8 compliance; use `black` for formatting
- **Type Hints**: Mandatory for all functions and methods
- **Docstrings**: Required for public functions (Google style)
- **Error Handling**: Specific exception types; log all errors with context
- **Async/Await**: Use async patterns for I/O operations (DB, API calls)
- **Import Order**: stdlib → third-party → local (enforced by isort)

### TypeScript (Frontend)
- **Style**: ESLint + Prettier configuration
- **Type Safety**: Strict mode enabled; no `any` types without justification
- **Components**: Functional components with TypeScript interfaces
- **Naming**: PascalCase for components, camelCase for functions/variables
- **Error Handling**: Try-catch for async operations; user-friendly error messages

### Database
- **Naming**: snake_case for tables and columns
- **Indexes**: Add indexes for frequently queried columns (user_id, created_at)
- **Constraints**: Use NOT NULL, UNIQUE, CHECK where applicable
- **Migrations**: Never edit existing migrations; create new ones for changes

## Performance Requirements

### Response Time
- Chat API endpoint: <2 seconds for NL query processing
- Database queries: <500ms for CRUD operations
- Agent tool calls: <1 second per MCP tool invocation

### Scalability
- Support 100 concurrent users without degradation
- Stateless design enables horizontal scaling
- Database connection pooling (max 20 connections per instance)

### Resource Limits
- Agent context window: 8K tokens (Cohere command-r)
- Max conversation history: 50 messages (prune older messages)
- Task list limit: 1000 tasks per user

## Development Workflow

### Feature Implementation Flow
1. **Specification**: Run `/sp.specify` to create detailed spec.md
2. **Clarification**: Run `/sp.clarify` for any ambiguous requirements
3. **Planning**: Run `/sp.plan` to generate architecture and design decisions
4. **Task Breakdown**: Run `/sp.tasks` to create testable tasks
5. **ADR Review**: Suggest `/sp.adr` for significant architectural decisions (wait for user consent)
6. **Implementation**: Run `/sp.implement` to execute tasks
7. **Commit & PR**: Run `/sp.git.commit_pr` to create commits and pull requests
8. **PHR Creation**: Automatically create Prompt History Records for all work

### Code Review Requirements
- All code generated via Claude Code (no manual edits)
- Unit tests must pass before commit
- Type checking (mypy for Python, tsc for TypeScript) must pass
- No hardcoded credentials or secrets
- Database queries must filter by user_id for isolation
- Error messages must be user-friendly (no stack traces exposed)

### Testing Gates
- **Pre-commit**: Unit tests + linting
- **Pre-merge**: Integration tests + E2E tests
- **Pre-deployment**: Full test suite + manual smoke tests

## Security Requirements

### Authentication
- JWT tokens expire after 7 days
- Refresh token mechanism via Better Auth
- Tokens stored in httpOnly cookies (not localStorage for production)
- CSRF protection enabled for state-changing operations

### Authorization
- User ID extracted from JWT claims (sub field)
- All database queries scoped to authenticated user
- Admin endpoints protected by role-based access control (future)

### Data Protection
- Passwords hashed with bcrypt (managed by Better Auth)
- Sensitive data encrypted at rest (Neon managed)
- TLS 1.2+ for all API communication
- No logging of JWT tokens or passwords

### Input Validation
- Pydantic models validate all request bodies
- SQL injection prevention via parameterized queries (SQLModel ORM)
- XSS prevention via React's built-in escaping
- Rate limiting on API endpoints (future enhancement)

## Observability

### Logging
- Structured JSON logs for production
- Log levels: DEBUG (dev), INFO (prod), WARNING (alerts), ERROR (incidents)
- Include user_id, request_id, timestamp in all logs
- Never log sensitive data (tokens, passwords)

### Monitoring (Future)
- Health check endpoint: GET /health (returns 200 if DB accessible)
- Metrics: request count, latency, error rate, active users
- Alerts: >5% error rate, >3s avg latency, DB connection failures

### Debugging
- Agent tool calls logged with input/output for debugging
- Conversation history stored in DB for issue reproduction
- Error traces captured with Sentry (future integration)

## Governance

### Constitution Authority
- This constitution supersedes all coding preferences and defaults
- All implementations must comply with these principles
- Non-compliance must be justified in ADR with user approval

### Amendment Process
- Amendments require `/sp.constitution` command
- Changes documented with rationale and migration plan
- Version number incremented (MAJOR.MINOR.PATCH)

### Compliance Verification
- Claude Code agents verify compliance before code generation
- PRs include checklist referencing constitution sections
- Constitution violations flagged during code review

### Decision Escalation
- Ambiguous requirements → Use AskUserQuestion tool
- Architectural decisions → Suggest `/sp.adr` and wait for user consent
- Constitution conflicts → Halt work and request clarification

**Version**: 1.0.0 | **Ratified**: 2026-01-16 | **Last Amended**: 2026-01-16
