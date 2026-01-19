"""Chat API endpoint for AI-powered todo management.

This module provides the REST API for the chatbot interface, integrating
JWT authentication, conversation persistence, and the AI agent.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models import get_session, Conversation, Message
from app.auth import get_current_user_id
from app.agent import run_agent


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    query: str = Field(..., max_length=2000, description="User's natural language query")
    conversation_id: Optional[int] = Field(None, description="Optional conversation ID to continue existing conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Add task to buy groceries tomorrow",
                "conversation_id": None
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Agent's natural language response")
    conversation_id: int = Field(..., description="Conversation ID for this exchange")
    tasks: Optional[List[Dict[str, Any]]] = Field(None, description="Optional list of tasks if relevant")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata (tokens used, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Done! I've added 'Buy groceries' to your tasks, due tomorrow.",
                "conversation_id": 1,
                "tasks": None,
                "metadata": None
            }
        }


# Router
router = APIRouter()


@router.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Process natural language chat query",
    description="""
    Process a user's natural language query and execute appropriate todo operations.

    **Authentication**: Requires valid JWT token in Authorization header.

    **User Isolation**: The user_id in the path must match the authenticated user from JWT.

    **Conversation Persistence**: Optionally provide conversation_id to continue an existing conversation.
    """
)
async def process_chat(
    user_id: int,
    request: ChatRequest,
    authenticated_user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """
    Process chat query with AI agent.

    Args:
        user_id: User ID from path parameter
        request: Chat request with query and optional conversation_id
        authenticated_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        ChatResponse with agent's response and conversation ID

    Raises:
        HTTPException 403: If user_id doesn't match authenticated user
        HTTPException 404: If conversation_id provided but not found
        HTTPException 400: If query is empty or invalid
    """
    # Verify user_id matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User ID mismatch. Cannot access resources for user {user_id}"
        )

    # Validate query
    if not request.query or len(request.query.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )

    # Get or create conversation
    conversation = None
    conversation_history = []

    if request.conversation_id:
        # Continue existing conversation
        conversation = session.get(Conversation, request.conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {request.conversation_id} not found"
            )

        # Verify conversation belongs to user
        if conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Conversation {request.conversation_id} does not belong to user {user_id}"
            )

        # Load conversation history (last 10 messages for context)
        from sqlmodel import select
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == request.conversation_id)
            .order_by(Message.created_at.asc())
            .limit(10)
        ).all()

        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    else:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.query
    )
    session.add(user_message)
    session.commit()

    # Run AI agent
    try:
        agent_response = await run_agent(
            query=request.query,
            user_id=user_id,
            db_session=session,
            conversation_history=conversation_history
        )
    except Exception as e:
        # Log error and return friendly message
        agent_response = f"I apologize, but I encountered an error processing your request. Please try again. (Error: {str(e)})"

    # Store agent response
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=agent_response
    )
    session.add(assistant_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.commit()

    # Return response
    return ChatResponse(
        response=agent_response,
        conversation_id=conversation.id,
        tasks=None,  # Could optionally query recent tasks here
        metadata=None  # Could add token usage, processing time, etc.
    )
