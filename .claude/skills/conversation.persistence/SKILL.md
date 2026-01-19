---
name: conversation.persistence
description: "Implement stateless conversation management by persisting chat history to the database, enabling conversation resumption and context retention across requests. Use when implementing chat endpoint state management, storing/retrieving conversation history, managing multiple conversations per user, or debugging conversation context issues."
category: Database / State Management
complexity: Medium
phase: 3
dependencies: ["SQLModel", "Neon PostgreSQL", "FastAPI"]
---

# Skill: Conversation Persistence

**Category**: Database / State Management
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: SQLModel, Neon PostgreSQL

## Purpose

Implement stateless conversation management by persisting chat history to the database, enabling conversation resumption and context retention across requests.

## When to Use

- Implementing chat endpoint state management
- Storing/retrieving conversation history
- Managing multiple conversations per user
- Debugging conversation context issues

## Pattern

### 1. Database Models

```python
# backend/app/models.py
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Conversation(SQLModel, table=True):
    """Conversation session for a user."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    """Individual message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)  # For quick user filtering
    role: MessageRole
    content: str = Field(max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional: store tool calls metadata
    tool_calls: Optional[str] = Field(default=None)  # JSON string

    # Relationships
    conversation: Optional[Conversation] = Relationship(back_populates="messages")
```

### 2. Conversation Service

```python
# backend/app/services/conversation_service.py
from sqlmodel import Session, select
from app.models import Conversation, Message, MessageRole
from app.database import get_session
from typing import Optional, List, Dict
from datetime import datetime
import json

def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create new one.

    Args:
        user_id: User ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation instance
    """
    with get_session() as session:
        if conversation_id:
            # Fetch existing conversation
            conversation = session.get(Conversation, conversation_id)

            # Verify ownership
            if not conversation or conversation.user_id != user_id:
                raise ValueError("Conversation not found or unauthorized")

            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

            return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        return conversation

def save_message(
    conversation_id: int,
    user_id: str,
    role: MessageRole,
    content: str,
    tool_calls: Optional[List[Dict]] = None
) -> Message:
    """
    Save a message to the database.

    Args:
        conversation_id: Conversation ID
        user_id: User ID
        role: Message role (user/assistant)
        content: Message content
        tool_calls: Optional tool execution metadata

    Returns:
        Created Message instance
    """
    with get_session() as session:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_calls=json.dumps(tool_calls) if tool_calls else None
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        return message

def get_conversation_history(
    conversation_id: int,
    limit: int = 20
) -> List[Dict[str, str]]:
    """
    Retrieve conversation history for agent context.

    Args:
        conversation_id: Conversation ID
        limit: Maximum number of messages to retrieve (default 20)

    Returns:
        List of messages in format: [{"role": "user", "content": "..."}]
    """
    with get_session() as session:
        # Get last N messages, ordered by creation time
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        messages = session.exec(statement).all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        # Format for AI agent
        return [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]

def list_user_conversations(
    user_id: str,
    limit: int = 10
) -> List[Conversation]:
    """
    List all conversations for a user.

    Args:
        user_id: User ID
        limit: Maximum number of conversations

    Returns:
        List of Conversation instances
    """
    with get_session() as session:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        return session.exec(statement).all()

def delete_conversation(conversation_id: int, user_id: str) -> bool:
    """
    Delete a conversation and all its messages.

    Args:
        conversation_id: Conversation ID
        user_id: User ID (for authorization)

    Returns:
        True if deleted, False otherwise
    """
    with get_session() as session:
        conversation = session.get(Conversation, conversation_id)

        if not conversation or conversation.user_id != user_id:
            return False

        # Delete all messages (cascade should handle this)
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = session.exec(statement).all()
        for msg in messages:
            session.delete(msg)

        # Delete conversation
        session.delete(conversation)
        session.commit()

        return True
```

### 3. Database Migration

```python
# backend/app/database.py
from sqlmodel import create_engine, SQLModel, Session
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def create_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    """Context manager for database sessions."""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
```

### 4. Integration with Chat Endpoint

```python
# backend/app/routes/chat.py (updated)
from app.services.conversation_service import (
    get_or_create_conversation,
    save_message,
    get_conversation_history
)
from app.models import MessageRole

@router.post("/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Stateless chat endpoint."""

    # 1. Get or create conversation
    conversation = get_or_create_conversation(
        user_id=user_id,
        conversation_id=request.conversation_id
    )

    # 2. Fetch history from database
    history = get_conversation_history(conversation.id, limit=20)

    # 3. Save user message
    save_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role=MessageRole.USER,
        content=request.message
    )

    # 4. Process with AI agent (using history)
    agent = create_agent()
    assistant_response, tool_calls = await process_message(
        agent=agent,
        message=request.message,
        conversation_history=history,
        user_id=user_id
    )

    # 5. Save assistant response
    save_message(
        conversation_id=conversation.id,
        user_id=user_id,
        role=MessageRole.ASSISTANT,
        content=assistant_response,
        tool_calls=tool_calls
    )

    # 6. Return response (server holds NO state)
    return {
        "conversation_id": conversation.id,
        "response": assistant_response,
        "tool_calls": tool_calls
    }
```

## Acceptance Criteria

- [ ] Conversations created per user
- [ ] Messages stored with correct role (user/assistant)
- [ ] Conversation history limited to last 20 messages for performance
- [ ] User isolation enforced (user_id checked)
- [ ] Timestamps automatically set on create/update
- [ ] Tool call metadata stored in messages
- [ ] Server remains stateless (no in-memory state)
- [ ] Conversation resumption works after server restart

## Database Schema

```sql
-- conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## Testing

```python
# test_conversation_service.py
import pytest
from app.services.conversation_service import (
    get_or_create_conversation,
    save_message,
    get_conversation_history
)
from app.models import MessageRole

def test_create_conversation():
    conv = get_or_create_conversation(user_id="test-user")
    assert conv.id is not None
    assert conv.user_id == "test-user"

def test_save_message():
    conv = get_or_create_conversation(user_id="test-user")
    msg = save_message(
        conversation_id=conv.id,
        user_id="test-user",
        role=MessageRole.USER,
        content="Hello"
    )
    assert msg.id is not None
    assert msg.content == "Hello"

def test_conversation_history():
    conv = get_or_create_conversation(user_id="test-user")
    save_message(conv.id, "test-user", MessageRole.USER, "Message 1")
    save_message(conv.id, "test-user", MessageRole.ASSISTANT, "Response 1")

    history = get_conversation_history(conv.id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
```

## Performance Considerations

- **History Limit**: Retrieve only last 20 messages to avoid large context windows
- **Indexing**: Index `conversation_id` and `user_id` columns for fast queries
- **Cascade Delete**: Use ON DELETE CASCADE for automatic message cleanup
- **Connection Pooling**: Use SQLModel with connection pool for Neon DB
- **Pagination**: Implement pagination for conversation list

## Common Issues

1. **Context too large**: Limit history to 20 messages, summarize older messages
2. **Slow queries**: Ensure indexes on conversation_id and user_id
3. **Orphaned messages**: Use CASCADE delete constraints
4. **Memory leaks**: Always use context manager for sessions
5. **Timezone issues**: Store all timestamps in UTC

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- Phase 3 Spec: `specs/phase3/database-schema.md`
- Related Skills: `ai.agent.integration.md`, `db.task.operations.md`

## Version

1.0.0 - Initial Phase 3 implementation
