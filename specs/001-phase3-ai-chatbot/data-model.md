# Data Model: AI-Powered Todo Chatbot - Phase 3

**Feature**: 001-phase3-ai-chatbot
**Date**: 2026-01-16
**Phase**: 1 - Database Schema Design

## Overview

This document defines the complete database schema for Phase 3, including entities, relationships, validation rules, and indexes for optimal performance. All models use SQLModel for type-safe ORM operations with Neon PostgreSQL.

## Entity Relationship Diagram (Text)

```
┌─────────────┐
│    User     │ (Managed by Better Auth)
│─────────────│
│ id (PK)     │
│ email       │
│ password    │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────┴──────────────┐
│                     │
│                     │
┌──────▼──────┐  ┌───▼────────────┐
│    Task     │  │  Conversation  │
│─────────────│  │────────────────│
│ id (PK)     │  │ id (PK)        │
│ user_id (FK)│  │ user_id (FK)   │
│ title       │  │ created_at     │
│ description │  │ updated_at     │
│ priority    │  └────────┬───────┘
│ tags (JSON) │           │
│ due_date    │           │ 1:N
│ status      │           │
│ recurring   │  ┌────────▼───────┐
│ created_at  │  │    Message     │
│ updated_at  │  │────────────────│
└─────────────┘  │ id (PK)        │
                 │ conversation_id│
                 │ user_id (FK)   │
                 │ role           │
                 │ content        │
                 │ created_at     │
                 └────────────────┘
```

## Entities

### 1. User (Managed by Better Auth)

**Purpose**: Store user authentication and profile information

**Note**: This table is managed by Better Auth. We only reference it via foreign keys.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email for login |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last profile update |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE index on `email`

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Password minimum 8 characters, Better Auth enforces

---

### 2. Task

**Purpose**: Store todo tasks with full metadata for task management

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List
from datetime import datetime

class Task(SQLModel, table=True):
    """Todo task model with user isolation."""

    __tablename__ = "tasks"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner of this task (enforces user isolation)"
    )

    # Core fields
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Task title (e.g., 'Buy groceries')"
    )

    description: str = Field(
        default="",
        description="Optional task description with details"
    )

    priority: str = Field(
        default="medium",
        max_length=20,
        description="Priority level: low, medium, high"
    )

    tags: List[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Tags for organization (e.g., ['work', 'urgent'])"
    )

    due_date: Optional[datetime] = Field(
        default=None,
        description="Task deadline (ISO format, nullable)"
    )

    status: bool = Field(
        default=False,
        description="Completion status (False=incomplete, True=complete)"
    )

    recurring: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Recurrence pattern (e.g., 'daily', 'weekly', 'monthly')"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Task creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last modification timestamp"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 42,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and coffee",
                "priority": "high",
                "tags": ["shopping", "urgent"],
                "due_date": "2026-01-17T18:00:00Z",
                "status": False,
                "recurring": None,
                "created_at": "2026-01-16T10:00:00Z",
                "updated_at": "2026-01-16T10:00:00Z"
            }
        }
```

**Validation Rules**:
- `title`: Required, max 255 characters, no leading/trailing whitespace
- `priority`: Must be one of `["low", "medium", "high"]` (validated in Pydantic schema)
- `tags`: Array of strings, max 10 tags per task, each tag max 50 characters
- `due_date`: Must be future datetime or NULL, ISO 8601 format
- `status`: Boolean only (False/True)
- `recurring`: Must match pattern `^(daily|weekly|monthly|yearly)$` or NULL
- `user_id`: Must reference existing user.id

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for fast filtering by user)
- INDEX on `created_at` (for date range queries)
- COMPOSITE INDEX on `(user_id, status)` (for "show incomplete tasks" queries)
- COMPOSITE INDEX on `(user_id, priority)` (for priority filtering)

**Constraints**:
- FOREIGN KEY `user_id` REFERENCES `user(id)` ON DELETE CASCADE
- CHECK `priority IN ('low', 'medium', 'high')`
- CHECK `LENGTH(title) > 0`
- CHECK `due_date IS NULL OR due_date > created_at`

---

### 3. Conversation

**Purpose**: Group related chat messages into conversation sessions

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    """Chat conversation session model."""

    __tablename__ = "conversations"

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner of this conversation"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Conversation start time"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Last message timestamp"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 42,
                "created_at": "2026-01-16T10:00:00Z",
                "updated_at": "2026-01-16T10:15:30Z"
            }
        }
```

**Validation Rules**:
- `user_id`: Must reference existing user.id
- `created_at`: Auto-set on creation, immutable
- `updated_at`: Auto-updated on any message addition

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for loading user's conversations)
- INDEX on `updated_at` (for sorting by recent activity)

**Constraints**:
- FOREIGN KEY `user_id` REFERENCES `user(id)` ON DELETE CASCADE
- CHECK `updated_at >= created_at`

**Business Rules**:
- One active conversation per user at a time (enforced in application logic)
- Conversations never deleted, only messages pruned after 50 messages
- `updated_at` refreshed on every new message

---

### 4. Message

**Purpose**: Store individual chat messages within conversations

**SQLModel Definition**:
```python
from sqlalchemy import TEXT

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
        description="Conversation this message belongs to"
    )

    user_id: int = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Message author (for user isolation)"
    )

    # Core fields
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message sender: 'user' or 'assistant'"
    )

    content: str = Field(
        sa_column=Column(TEXT),
        nullable=False,
        description="Message text content (supports long messages)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message send time"
    )

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "user_id": 42,
                "role": "user",
                "content": "Add task to buy groceries tomorrow",
                "created_at": "2026-01-16T10:00:00Z"
            }
        }
```

**Validation Rules**:
- `role`: Must be one of `["user", "assistant"]` (validated in Pydantic)
- `content`: Required, max 10,000 characters (Cohere 8K token limit)
- `conversation_id`: Must reference existing conversation.id
- `user_id`: Must reference existing user.id
- `created_at`: Immutable after creation

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `conversation_id` (for loading conversation history)
- INDEX on `user_id` (for user isolation queries)
- INDEX on `created_at` (for ordering messages chronologically)
- COMPOSITE INDEX on `(conversation_id, created_at)` (for pagination)

**Constraints**:
- FOREIGN KEY `conversation_id` REFERENCES `conversations(id)` ON DELETE CASCADE
- FOREIGN KEY `user_id` REFERENCES `user(id)` ON DELETE CASCADE
- CHECK `role IN ('user', 'assistant')`
- CHECK `LENGTH(content) > 0`

**Business Rules**:
- Messages immutable after creation (no updates, only inserts)
- Messages deleted when parent conversation deleted (CASCADE)
- Maximum 50 messages loaded per conversation (application enforces)
- Older messages pruned but archived (future enhancement)

---

## Relationships

### User ↔ Task (1:N)
- One user owns many tasks
- Tasks cannot exist without a user (CASCADE DELETE)
- All task queries must filter by `user_id`

### User ↔ Conversation (1:N)
- One user has many conversations
- Conversations deleted when user deleted (CASCADE DELETE)
- Active conversation identified by most recent `updated_at`

### Conversation ↔ Message (1:N)
- One conversation contains many messages
- Messages deleted when conversation deleted (CASCADE DELETE)
- Messages ordered by `created_at` ASC for display

### User ↔ Message (1:N)
- One user authors many messages
- User can see only their own messages (isolation)
- Messages deleted when user deleted (CASCADE DELETE)

---

## Database Migrations

### Initial Schema Creation

```sql
-- Create users table (managed by Better Auth)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL CHECK (LENGTH(title) > 0),
    description TEXT DEFAULT '',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    tags JSONB DEFAULT '[]',
    due_date TIMESTAMP,
    status BOOLEAN NOT NULL DEFAULT FALSE,
    recurring VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (due_date IS NULL OR due_date > created_at)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);

-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (updated_at >= created_at)
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (LENGTH(content) > 0),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

### SQLModel Auto-Migration

```python
from sqlmodel import SQLModel, create_engine
import os

# Create engine with Neon connection
engine = create_engine(os.environ["DATABASE_URL"])

# Create all tables
SQLModel.metadata.create_all(engine)
```

---

## Query Patterns

### Common Queries

**1. Get user's incomplete tasks ordered by priority**:
```python
from sqlmodel import select

statement = (
    select(Task)
    .where(Task.user_id == user_id, Task.status == False)
    .order_by(Task.priority.desc(), Task.due_date.asc())
)
tasks = session.exec(statement).all()
```

**2. Search tasks by keyword**:
```python
statement = (
    select(Task)
    .where(
        Task.user_id == user_id,
        (Task.title.ilike(f"%{query}%") | Task.description.ilike(f"%{query}%"))
    )
)
tasks = session.exec(statement).all()
```

**3. Get conversation history (last 50 messages)**:
```python
statement = (
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(50)
)
messages = session.exec(statement).all()
messages.reverse()  # Oldest first for display
```

**4. Create new task**:
```python
task = Task(
    user_id=user_id,
    title="Buy groceries",
    priority="high",
    tags=["shopping", "urgent"],
    due_date=datetime(2026, 1, 17, 18, 0)
)
session.add(task)
session.commit()
session.refresh(task)
return task.id
```

---

## Performance Considerations

### Index Strategy
- **Covered Queries**: Composite indexes for common filter combinations
- **Selective Indexes**: Index only frequently queried columns
- **Avoid Over-Indexing**: Each index adds write overhead

### Query Optimization
- **Batch Operations**: Use `session.add_all()` for bulk inserts
- **Lazy Loading**: Use `select()` with explicit joins, avoid N+1 queries
- **Pagination**: LIMIT + OFFSET for large result sets (conversations)

### Data Volume Estimates
- **Tasks**: ~1000 tasks per user × 1000 users = 1M rows (manageable)
- **Messages**: ~50 messages per conversation × 10 conversations per user × 1000 users = 500K rows
- **Conversations**: ~10 per user × 1000 users = 10K rows

### Archival Strategy (Future)
- Archive messages older than 90 days to separate table
- Keep last 50 messages per conversation in hot storage
- Implement on-demand message history retrieval

---

## Security Considerations

### User Isolation
- **Application Level**: All queries filter by `user_id` from JWT
- **Database Level**: Foreign key constraints enforce referential integrity
- **Testing**: Security audit tests verify no cross-user access

### Data Encryption
- **At Rest**: Neon PostgreSQL handles encryption automatically
- **In Transit**: TLS 1.2+ for all database connections
- **Sensitive Fields**: Passwords hashed via Better Auth (bcrypt)

### Audit Trail
- **created_at**: Track entity creation time
- **updated_at**: Track last modification (future: add modified_by user_id)
- **Soft Deletes**: Future enhancement for task/conversation recovery

---

## Testing Strategy

### Unit Tests
- Test SQLModel model validation (invalid priority, missing title)
- Test foreign key constraints (orphaned tasks)
- Test check constraints (due_date < created_at)

### Integration Tests
- Test CRUD operations with real database (SQLite in-memory)
- Test transaction rollback on errors
- Test concurrent access (multiple users)

### Data Migration Tests
- Test schema creation from scratch
- Test backward compatibility (add columns without breaking)
- Test data integrity after migrations

---

## Conclusion

The data model supports all Phase 3 requirements:
- ✅ User isolation via user_id foreign keys
- ✅ Conversation persistence for stateless architecture
- ✅ Efficient queries via strategic indexes
- ✅ Type safety via SQLModel Pydantic integration
- ✅ Scalability to 1000+ users with proper indexing

Next step: Generate API contracts in `/contracts/` directory.
