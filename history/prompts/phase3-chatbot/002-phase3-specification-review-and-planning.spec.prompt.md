---
id: 002
title: Phase 3 Specification Review and Planning
stage: spec
date: 2026-01-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase3-chatbot
branch: master
user: DELL
command: /sp.specify
labels: ["phase3", "ai-chatbot", "specification", "planning", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/phase3-chatbot/002-phase3-specification-review-and-planning.spec.prompt.md
tests:
  - None (specification phase)
---

## Prompt

User executed `/sp.specify` command with comprehensive specification for Phase 3 AI-powered Todo Chatbot. The specification includes:

**Overview**: Extend Phase 2 full-stack app into AI-powered conversational chatbot managing Todo lists via natural language, using OpenAI ChatKit (frontend), OpenAI Agents SDK with Cohere API (backend agent logic), and Official MCP SDK (stateless tool integrations).

**Key Requirements**:
- **Functional**: NL query handling for all Todo features, destructive action confirmation, conversation history resumption from DB
- **Non-Functional**: <2s response time, 100 concurrent users, JWT verification, stateless design, cross-browser compatibility, WCAG 2.1 compliance, 80% test coverage

**Architecture**:
- **Frontend**: Next.js App Router with ChatKit embedded via navbar icon
- **Backend**: FastAPI with JWT auth calling OpenAI Agents (Cohere-adapted) and MCP tools
- **Database**: Neon PostgreSQL with SQLModel (Task, Conversation, Message models)
- **AI Layer**: Agents SDK runner for NL parsing/tool calls using Cohere as model provider
- **Flow**: User NL → ChatKit → /api/{user_id}/chat (JWT) → Agent run (Cohere) → MCP tools → DB → Response

**MCP Tools Specification**: Define stateless tools (add_task, delete_task, update_task, list_tasks, complete_task, search_tasks) with SQLModel integration, using UV package manager for dependencies (uv add agents cohere fastapi sqlmodel).

**Authentication**: Better Auth + JWT (7-day expiry, shared secret via env)

**Database Schema**: SQLModel models for Task (with user_id, recurring support), Conversation (with history JSON), Message (with timestamp)

**Bonus Features**: Reusable intelligence (subagents/skills), multi-language (Urdu via Cohere), voice commands (SpeechRecognition API), cloud-native blueprints (Helm charts)

## Response snapshot

**Project Structure Explored**:
- Backend: Empty scaffolding (no Phase 2 implementation)
- Frontend: Partial setup (UI component library, API client with JWT support, Next.js 16.1.1, React 19.2.3)
- Phase 2 NOT implemented (should have been prerequisite with CRUD APIs, web UI)
- Dependencies: Frontend configured, backend requirements.txt empty
- Authentication: Framework configured but not implemented
- Database: Models specified but not created yet

**Critical Assessment**: This is a greenfield Phase 3 project with only foundational configuration. Phase 2 full-stack implementation is missing (CRUD APIs, database models, web UI).

**Implementation Plan Created**: 17-task todo list covering:
1. Constitution and standards setup
2. Backend FastAPI structure with UV
3. SQLModel database models
4. MCP server with task operation tools
5. OpenAI Agents SDK + Cohere integration
6. JWT authentication middleware
7. Chat API endpoint implementation
8. Conversation history persistence
9. Better Auth frontend setup
10. ChatKit UI integration
11. Chat icon trigger in navbar
12. API connection with JWT headers
13. Unit tests for MCP tools/APIs
14. E2E tests for NL scenarios
15. Neon DB setup and migrations
16. Environment configuration
17. End-to-end testing

**Key Architectural Decisions Identified** (require ADRs):
1. Using Cohere instead of Gemini for enhanced NL processing
2. Stateless chatbot design with DB persistence for conversations
3. UV package manager for Python dependencies
4. OpenAI ChatKit for frontend chat interface
5. Official MCP SDK for tool integrations
6. SQLModel ORM with Neon PostgreSQL

## Outcome

- ✅ Impact: Comprehensive specification reviewed, project structure explored, greenfield status confirmed, implementation roadmap created with 17 actionable tasks
- 🧪 Tests: Test strategy defined (80% coverage requirement, unit tests for tools/APIs, E2E for NL scenarios)
- 📁 Files: PHR created at history/prompts/phase3-chatbot/002-phase3-specification-review-and-planning.spec.prompt.md
- 🔁 Next prompts:
  1. Create project constitution with code standards
  2. Set up backend FastAPI structure
  3. Define SQLModel database models
  4. Suggest ADRs for 6 architectural decisions identified
- 🧠 Reflection: Specification is well-structured with detailed architecture, code examples, and tool definitions. Missing Phase 2 foundation will require building CRUD operations from scratch. Cohere API integration adaptation is clearly specified with code examples.

## Evaluation notes (flywheel)

- Failure modes observed: None yet (planning phase)
- Graders run and results (PASS/FAIL): N/A (specification review)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin with constitution creation followed by backend structure setup to establish development standards before implementation
