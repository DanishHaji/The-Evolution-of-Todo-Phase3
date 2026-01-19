"""Database models for Phase 3 AI Todo Chatbot using SQLModel."""

from sqlmodel import SQLModel, Field, Column, JSON, create_engine, Session
from sqlalchemy import TEXT
from typing import Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database engine setup
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries in development
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)


# User model (managed by Better Auth, we only reference via FK)
class User(SQLModel, table=True):
    """User authentication model (managed by Better Auth)."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# Task model
class Task(SQLModel, table=True):
    """Todo task model with user isolation."""

    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    # Core fields
    title: str = Field(
        max_length=255,
        nullable=False,
    )

    description: str = Field(
        default="",
    )

    priority: str = Field(
        default="medium",
        max_length=20,
    )

    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )

    due_date: Optional[datetime] = Field(
        default=None,
    )

    status: bool = Field(
        default=False,
    )

    recurring: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )


# Conversation model
class Conversation(SQLModel, table=True):
    """Chat conversation session model."""

    __tablename__ = "conversations"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
    )


# Message model
class Message(SQLModel, table=True):
    """Chat message model for conversation history."""

    __tablename__ = "messages"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
    )

    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False,
    )

    # Core fields
    role: str = Field(
        max_length=20,
        nullable=False,
    )

    content: str = Field(
        sa_column=Column(TEXT, nullable=False),
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
    )


def init_db():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")


def get_session():
    """Get database session for dependency injection."""
    with Session(engine) as session:
        yield session


if __name__ == "__main__":
    init_db()
