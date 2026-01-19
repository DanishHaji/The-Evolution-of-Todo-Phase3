# Quickstart Guide: Phase 3 AI Todo Chatbot

**Feature**: 001-phase3-ai-chatbot
**Date**: 2026-01-16
**Estimated Setup Time**: 15-20 minutes

## Prerequisites

- **Node.js**: 18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **Git**: For version control
- **Neon Account**: Free tier at https://neon.tech
- **Cohere API Key**: Free tier at https://cohere.com

## Quick Setup (5 Minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd "Phase 3"

# 2. Install UV (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Backend setup
cd backend
uv add fastapi uvicorn sqlmodel psycopg2-binary pydantic python-dotenv
uv add agents cohere
uv add --dev pytest pytest-asyncio httpx black isort mypy

# 4. Frontend setup
cd ../frontend
npm install

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section below)

# 6. Run database migrations
cd ../backend
uv run python -c "from main import init_db; init_db()"

# 7. Start services
# Terminal 1 (Backend):
cd backend
uv run uvicorn main:app --reload --port 8000

# Terminal 2 (Frontend):
cd frontend
npm run dev

# 8. Open browser
# Navigate to http://localhost:3000
```

---

## Detailed Setup Instructions

### Step 1: Environment Setup

#### 1.1 Install UV (Python Package Manager)

**macOS/Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify Installation**:
```bash
uv --version
# Expected output: uv 0.1.x
```

#### 1.2 Install Node.js

Download from https://nodejs.org/ (LTS version 18+)

**Verify Installation**:
```bash
node --version  # Should be 18+
npm --version   # Should be 9+
```

---

### Step 2: Database Setup (Neon PostgreSQL)

#### 2.1 Create Neon Account

1. Visit https://neon.tech
2. Sign up with GitHub (or email)
3. Create new project: "Phase3-Todo-Chatbot"
4. Select region closest to you
5. Copy connection string

#### 2.2 Get Database URL

Your connection string format:
```
postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

**Save this for .env configuration!**

---

### Step 3: Get API Keys

#### 3.1 Cohere API Key

1. Visit https://cohere.com
2. Sign up for free account
3. Navigate to API Keys section
4. Generate new API key
5. Copy key (starts with `co_...`)

#### 3.2 JWT Secret

Generate a secure random string:
```bash
openssl rand -hex 32
```

Copy the output for JWT_SECRET

---

### Step 4: Configure Environment Variables

#### 4.1 Backend Configuration

Create `backend/.env`:
```bash
# Database
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Authentication
JWT_SECRET=your-generated-hex-string-from-openssl
BETTER_AUTH_SECRET=your-another-secure-random-string

# AI Model
COHERE_API_KEY=co_your_cohere_api_key_here

# Environment
ENV=development
DEBUG=true
```

#### 4.2 Frontend Configuration

Create `frontend/.env.local`:
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Optional: OpenAI ChatKit (if using their hosted version)
NEXT_PUBLIC_OPENAI_API_KEY=your-openai-key-if-needed
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-if-needed
```

---

### Step 5: Backend Setup

#### 5.1 Install Dependencies

```bash
cd backend

# Core dependencies
uv add fastapi uvicorn[standard] sqlmodel psycopg2-binary pydantic python-dotenv

# AI dependencies
uv add agents cohere

# Development dependencies
uv add --dev pytest pytest-asyncio httpx black isort mypy
```

#### 5.2 Project Structure

Create the following structure:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entrypoint
│   ├── models.py            # SQLModel database models
│   ├── auth.py              # JWT middleware
│   ├── chat.py              # Chat endpoint
│   ├── agent.py             # OpenAI Agents + Cohere setup
│   └── mcp_tools.py         # MCP tool definitions
├── tests/
│   ├── __init__.py
│   ├── test_tools.py        # Tool unit tests
│   └── test_api.py          # API integration tests
├── .env                     # Environment variables
├── pyproject.toml           # UV project config
└── README.md
```

#### 5.3 Initialize Database

Create `backend/app/main.py`:
```python
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Create all tables."""
    from app.models import Task, Conversation, Message
    SQLModel.metadata.create_all(engine)

# FastAPI app
app = FastAPI(title="Phase 3 AI Todo Chatbot API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}
```

Run migrations:
```bash
uv run python -c "from app.main import init_db; init_db()"
```

Expected output:
```
CREATE TABLE users ...
CREATE TABLE tasks ...
CREATE TABLE conversations ...
CREATE TABLE messages ...
```

---

### Step 6: Frontend Setup

#### 6.1 Install Dependencies

```bash
cd frontend

# Install all dependencies from package.json
npm install

# Additional dependencies if needed
npm install @openai/chatkit better-auth
```

#### 6.2 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with ChatKit
│   ├── page.tsx             # Home page
│   └── api/
│       └── auth/
│           └── route.ts     # Better Auth API route
├── components/
│   ├── ui/                  # Radix UI components (existing)
│   ├── ChatbotIcon.tsx      # Floating chat icon
│   ├── ChatbotModal.tsx     # ChatKit modal wrapper
│   └── AuthProvider.tsx     # Better Auth context
├── lib/
│   ├── api.ts               # API client (existing)
│   └── auth.ts              # Better Auth client
├── .env.local               # Environment variables
└── package.json
```

#### 6.3 Verify Frontend

```bash
npm run dev
```

Open http://localhost:3000 - you should see the Next.js welcome page.

---

### Step 7: Run Services

#### 7.1 Start Backend (Terminal 1)

```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Test health endpoint:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}
```

#### 7.2 Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Expected output:
```
 ▲ Next.js 16.1.1
 - Local:        http://localhost:3000
 - Ready in 2.3s
```

---

## Testing Setup

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_tools.py -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run E2E tests (requires backend running)
npm run test:e2e

# Run with Playwright UI
npm run test:e2e:ui
```

---

## Verification Checklist

After setup, verify:

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Database connection successful (check /health endpoint)
- [ ] Environment variables loaded correctly
- [ ] Database tables created (tasks, conversations, messages)
- [ ] Tests passing (pytest and npm test)

### Quick Verification Commands

```bash
# Backend health check
curl http://localhost:8000/health

# Database connection test
cd backend
uv run python -c "from sqlmodel import Session, create_engine; engine = create_engine(os.environ['DATABASE_URL']); Session(engine)"

# API test (should return 401 without JWT)
curl http://localhost:8000/api/1/chat -X POST -H "Content-Type: application/json" -d '{"query":"test"}'
```

---

## Common Issues & Troubleshooting

### Issue 1: UV Command Not Found

**Solution**:
```bash
# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Verify
uv --version
```

### Issue 2: Database Connection Failed

**Symptoms**: `Connection refused` or `Could not connect to server`

**Solution**:
1. Verify DATABASE_URL is correct in .env
2. Check Neon project is not paused (free tier auto-pauses)
3. Ensure `?sslmode=require` is at end of connection string
4. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Issue 3: Cohere API 401 Unauthorized

**Symptoms**: `401 Unauthorized` when making chat requests

**Solution**:
1. Verify COHERE_API_KEY in backend/.env
2. Check API key is active at https://cohere.com
3. Ensure key starts with `co_`
4. Test API key:
   ```bash
   curl https://api.cohere.ai/v1/models \
     -H "Authorization: Bearer $COHERE_API_KEY"
   ```

### Issue 4: Frontend Build Errors

**Symptoms**: `Module not found` or `Cannot find module '@openai/chatkit'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 5: JWT Token Invalid

**Symptoms**: 401 errors when calling chat API

**Solution**:
1. Ensure JWT_SECRET matches between frontend and backend
2. Verify token is not expired (7-day default)
3. Check Authorization header format: `Bearer <token>`
4. Test JWT decoding:
   ```python
   from jose import jwt
   token = "your-token-here"
   payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
   print(payload)
   ```

---

## Next Steps After Setup

### 1. Create First User

```bash
# Using Better Auth API
curl http://localhost:3000/api/auth/signup \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 2. Test Chat API

```bash
# Get JWT token first (from signup or login response)
TOKEN="your-jwt-token-here"

# Send chat query
curl http://localhost:8000/api/1/chat \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"Add task to buy groceries tomorrow"}'
```

### 3. Explore UI

1. Open http://localhost:3000
2. Click chat icon (bottom right)
3. Type: "Add task to buy groceries"
4. Verify task appears in UI

### 4. Run Test Suite

```bash
# Backend tests (should have 80%+ coverage)
cd backend
uv run pytest --cov=app --cov-report=term

# Frontend tests
cd frontend
npm test
```

---

## Development Workflow

### Making Changes

1. **Backend Code Changes**:
   - Edit files in `backend/app/`
   - Uvicorn auto-reloads on save
   - Run tests: `uv run pytest`
   - Format code: `uv run black . && uv run isort .`

2. **Frontend Code Changes**:
   - Edit files in `frontend/app/` or `frontend/components/`
   - Next.js Fast Refresh auto-updates browser
   - Run tests: `npm test`
   - Format code: `npm run lint:fix`

### Adding New MCP Tools

1. Define tool in `backend/app/mcp_tools.py`
2. Add to agent tools list in `backend/app/agent.py`
3. Write unit tests in `tests/test_tools.py`
4. Update agent instructions if needed

### Database Schema Changes

1. Modify models in `backend/app/models.py`
2. Generate migration (if using Alembic):
   ```bash
   alembic revision --autogenerate -m "Add new field"
   alembic upgrade head
   ```
3. Or use SQLModel auto-migration:
   ```python
   SQLModel.metadata.create_all(engine)
   ```

---

## Performance Tips

### Backend Optimization

- Use async database drivers (asyncpg) for better concurrency
- Enable connection pooling (default: 10 connections)
- Cache frequent queries (Redis, future enhancement)
- Monitor slow queries with `echo=True` in development

### Frontend Optimization

- Use Next.js Image component for optimized images
- Implement lazy loading for chat history (pagination)
- Debounce chat input to reduce API calls
- Use React.memo for expensive components

---

## Security Checklist

Before deploying to production:

- [ ] Change JWT_SECRET to strong random value
- [ ] Enable HTTPS only (no HTTP)
- [ ] Use httpOnly cookies for JWT (not localStorage)
- [ ] Enable CORS with specific origins
- [ ] Rate limit API endpoints (10 req/min per user)
- [ ] Rotate Cohere API key monthly
- [ ] Enable database backups (Neon automatic)
- [ ] Set up monitoring (Sentry, Datadog)

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Cohere API**: https://docs.cohere.com/
- **OpenAI Agents SDK**: https://github.com/openai/swarm
- **Better Auth**: https://www.better-auth.com/docs
- **UV Package Manager**: https://docs.astral.sh/uv/

---

## Support

For issues or questions:
1. Check [Common Issues](#common-issues--troubleshooting)
2. Review constitution: `.specify/memory/constitution.md`
3. Check spec: `specs/001-phase3-ai-chatbot/spec.md`
4. Create GitHub issue with logs

---

## Success Criteria

Setup complete when:
- ✅ Both backend and frontend running without errors
- ✅ Health check returns 200 OK
- ✅ Database tables created successfully
- ✅ Chat API accepts requests (with valid JWT)
- ✅ Tests passing (80%+ coverage)
- ✅ Can send chat message and receive response

**Estimated Total Setup Time**: 15-20 minutes
