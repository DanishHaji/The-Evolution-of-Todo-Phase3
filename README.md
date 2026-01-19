# The Evolution of Todo - Phase 3: AI-Powered Todo Chatbot

## Overview

Phase 3 transforms the Todo application into an AI-powered chatbot that allows users to manage their tasks through natural language conversations. The system integrates modern AI capabilities with a clean, responsive UI.

### Key Technologies
- **Frontend**: Next.js 16+ with React 19, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: Python FastAPI with Cohere AI API
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel
- **Authentication**: Better Auth with JWT tokens
- **AI Model**: Cohere Command-R (command-nightly)

## Features

### Phase 1 & 2 Features (Enhanced UI)
- ✅ User authentication (Register/Login)
- ✅ Create, read, update, and delete tasks
- ✅ Mark tasks as complete/incomplete
- ✅ Add task descriptions and due dates
- ✅ Filter tasks (All, Active, Completed)
- ✅ Real-time UI updates
- ✅ Beautiful gradient UI with animations
- ✅ Dark mode support
- ✅ Mobile responsive design

### Phase 3: AI Chatbot Features
- ✅ Natural language task management
- ✅ Conversational AI interface powered by Cohere
- ✅ Context-aware conversations with history persistence
- ✅ MCP (Model Context Protocol) tools integration
- ✅ Stateless architecture with database-backed conversations

## Project Structure

```
Phase 3/
├── frontend/              # Next.js 16+ with App Router
│   ├── app/
│   │   ├── auth/         # Authentication pages (login, register)
│   │   ├── dashboard/    # Main dashboard and chat interface
│   │   └── page.tsx      # Landing page
│   ├── components/
│   │   ├── auth/         # Auth components (ProtectedRoute)
│   │   ├── chat/         # Chat interface components
│   │   ├── tasks/        # Task management components
│   │   └── ui/           # Reusable UI components
│   ├── context/          # React context (AuthContext)
│   ├── lib/              # API utilities
│   └── styles/           # Global styles
├── backend/              # Python FastAPI
│   ├── app/
│   │   ├── api/          # REST API endpoints
│   │   ├── agent.py      # Cohere AI agent integration
│   │   ├── chat.py       # Chat endpoint
│   │   ├── mcp_tools.py  # MCP tool implementations
│   │   ├── models.py     # SQLModel database models
│   │   └── main.py       # FastAPI application
│   └── tests/            # Backend tests (61 tests passing)
├── specs/                # Feature specifications
├── history/              # Development history (PHRs, ADRs)
└── .specify/             # SpecKit Plus templates
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.13+
- UV (Python package manager)
- Cohere API key (free tier available)
- Neon PostgreSQL database (free tier available)

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/DanishHaji/The-Evolution-of-Todo-Phase3.git
cd The-Evolution-of-Todo-Phase3
```

#### 2. Backend Setup

```bash
cd backend

# Create .env file with your credentials
cat > .env << EOF
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
COHERE_API_KEY=your_cohere_api_key_here
JWT_SECRET=your_jwt_secret_here
EOF

# Install dependencies
uv venv
uv pip install -r requirements.txt

# Run database migrations
uv run python -c "from app.models import init_db; init_db()"

# Start backend server
uv run uvicorn app.main:app --reload --port 8000
```

Backend will run on `http://localhost:8000`

#### 3. Frontend Setup

```bash
cd frontend

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your_better_auth_secret
BETTER_AUTH_URL=http://localhost:3000
EOF

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:3000`

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
COHERE_API_KEY=your_cohere_api_key_here
JWT_SECRET=your_jwt_secret_here
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your_better_auth_secret
BETTER_AUTH_URL=http://localhost:3000
```

## API Documentation

### Authentication Endpoints

#### POST `/api/auth/register`
Register a new user
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### POST `/api/auth/login`
Login existing user
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Task Endpoints

#### GET `/api/tasks`
Get all tasks for authenticated user

#### POST `/api/tasks/`
Create a new task
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "due_date": "2024-12-25T10:00:00"
}
```

#### PATCH `/api/tasks/{task_id}`
Update a task
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "status": true
}
```

#### DELETE `/api/tasks/{task_id}`
Delete a task

### Chat Endpoint

#### POST `/api/{user_id}/chat`
Send message to AI chatbot
```json
{
  "query": "Add a task to buy groceries tomorrow",
  "conversation_id": 1  // Optional, for conversation context
}
```

## MCP Tools

The AI agent has access to these tools for task management:

| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create new task | `title`, `desc`, `priority`, `due_date` |
| `list_tasks` | Retrieve tasks with filters | `status`, `priority`, `limit` |
| `complete_task` | Mark task as complete | `task_id` |
| `update_task` | Modify task details | `task_id`, `title`, `description`, `status` |
| `delete_task` | Remove task | `task_id` |
| `search_tasks` | Search tasks by keyword | `query`, `limit` |

## Database Schema

### Users Table
- `id` (integer, PK, auto-increment)
- `email` (string, unique, required)
- `password` (string, hashed, required)
- `created_at`, `updated_at` (timestamps)

### Tasks Table
- `id` (string, UUID, PK)
- `user_id` (integer, FK to users)
- `title` (string, required)
- `description` (text, optional)
- `status` (boolean, default false)
- `priority` (string, optional: low/medium/high)
- `tags` (JSON array, optional)
- `due_date` (datetime, optional)
- `recurring` (JSON, optional)
- `created_at`, `updated_at` (timestamps)

### Conversations Table
- `id` (integer, PK, auto-increment)
- `user_id` (integer, FK to users)
- `created_at`, `updated_at` (timestamps)

### Messages Table
- `id` (integer, PK, auto-increment)
- `conversation_id` (integer, FK to conversations)
- `role` (enum: 'user' | 'assistant')
- `content` (text, required)
- `created_at` (timestamp)

## AI Agent Architecture

### Conversation Flow
```
1. User types message in chat interface
   ↓
2. Frontend sends POST /api/{user_id}/chat
   ↓
3. Backend retrieves conversation history from DB
   ↓
4. Cohere AI agent processes query with context
   ↓
5. Agent decides which MCP tool(s) to invoke
   ↓
6. Tools execute database operations
   ↓
7. Agent formulates natural language response
   ↓
8. Response stored in DB and returned to frontend
   ↓
9. Frontend displays response in chat
```

### Example Conversations

**Add Task:**
```
User: "Add a task to buy groceries tomorrow"
AI: "Done! I've added 'Buy groceries' to your tasks, due tomorrow."
```

**List Tasks:**
```
User: "Show me my high priority tasks"
AI: "You have 2 high priority tasks:
     1. Submit report (due Friday)
     2. Call dentist (no due date)"
```

**Complete Task:**
```
User: "Mark task 123 as complete"
AI: "Great! I've marked task 123 as completed."
```

**Delete All:**
```
User: "Delete all my tasks"
AI: "I found 5 tasks. Are you sure you want to delete all of them?"
User: "yes"
AI: "Done! I've deleted all 5 tasks."
```

## Development

### Backend Testing
```bash
cd backend
uv run pytest
# 61/61 tests passing ✅
```

### Frontend Development
```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # Run ESLint
```

### Code Quality
- TypeScript strict mode enabled
- ESLint with Next.js config
- Tailwind CSS for styling
- Framer Motion for animations

## Spec-Driven Development (SDD)

This project follows the **Spec-Driven Development** methodology:

1. **Specification Phase**: Write detailed specs in `specs/` directory
2. **Planning Phase**: Create implementation plans
3. **Task Breakdown**: Generate actionable tasks
4. **Implementation**: Code with Claude Code assistance
5. **Documentation**: Create PHRs (Prompt History Records)
6. **Decisions**: Document ADRs (Architecture Decision Records)

### Workflow
```bash
# Create new feature specification
/sp.specify "Feature description"

# Generate implementation plan
/sp.plan

# Create tasks breakdown
/sp.tasks

# Implement feature
/sp.implement

# Document decisions
/sp.adr "Decision title"
```

## Features Showcase

### Dashboard
- Real-time task filtering (All, Active, Completed)
- Beautiful statistics cards showing:
  - Total tasks count
  - Completed tasks count
  - Active tasks count
  - Completion percentage
- Task creation with title, description, and due date
- Instant updates without page refresh (auto-refresh every 2 seconds)

### Task Management
- Inline editing of tasks
- One-click completion toggle
- Task deletion with animation
- Due date display with formatting
- Hover effects and smooth transitions

### AI Chat Interface
- Natural language understanding
- Conversation history persistence
- Context-aware responses
- Tool invocation for task operations
- Error handling with friendly messages

## Troubleshooting

### Port Conflicts
If port 3000 is busy:
```bash
# Frontend will automatically use next available port (3001, 3002, 3003)
# Update CORS in backend/app/main.py if needed
```

### Database Connection
```bash
# Test database connection
cd backend
uv run python -c "from app.models import engine; from sqlalchemy import text; engine.connect().execute(text('SELECT 1'))"
```

### Cohere API Errors
- Check API key is valid in backend/.env
- Verify API quota/limits not exceeded
- Review backend logs for detailed error messages

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Write specifications first (SDD approach)
4. Implement with tests
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## License

This project is part of the Todo Evolution Hackathon.

## Resources

- [Cohere API Documentation](https://docs.cohere.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Neon PostgreSQL](https://neon.tech/)
- [Claude Code](https://claude.com/product/claude-code)
- [SpecKit Plus](https://github.com/panaversity/spec-kit-plus)

## Credits

Developed by Danish Haji using Spec-Driven Development methodology with Claude Code.

## Hackathon

This project is part of **Hackathon II - Todo Spec-Driven Development** organized by Panaversity.
