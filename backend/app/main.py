"""FastAPI application for Phase 3 AI Todo Chatbot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.chat import router as chat_router
from app.api.auth_api import router as auth_router
from app.api.tasks_api import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("Starting Phase 3 AI Todo Chatbot API...")
    # Note: Database migrations should be run separately before starting the app
    # Run: uv run python -c "from app.models import init_db; init_db()"
    yield
    # Shutdown
    print("Shutting down Phase 3 AI Todo Chatbot API...")


# Initialize FastAPI app
app = FastAPI(
    title="Phase 3 AI Todo Chatbot API",
    description="AI-powered todo management via natural language using Cohere API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js frontend (local)
        "http://localhost:3001",  # Alternative port
        "http://localhost:3002",  # Alternative port 2
        "http://localhost:3003",  # Alternative port 3
        "https://the-evolution-of-todo-phase3.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(chat_router, tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Phase 3 AI Todo Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - verify API and database connectivity."""
    # Try to check database connection
    try:
        from app.models import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e),
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
