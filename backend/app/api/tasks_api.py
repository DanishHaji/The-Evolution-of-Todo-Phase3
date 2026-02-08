"""Task management API endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Optional
from app.models import Task, engine
from app.auth import get_current_user_id

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: bool
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[TaskResponse])
async def get_tasks(user_id: int = Depends(get_current_user_id)):
    """Get all tasks for authenticated user."""
    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        tasks = session.exec(statement).all()

        return [
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                user_id=task.user_id,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new task."""
    with Session(engine) as session:
        new_task = Task(
            title=task_data.title,
            description=task_data.description,
            user_id=user_id,
            status=False
        )

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        return TaskResponse(
            id=new_task.id,
            title=new_task.title,
            description=new_task.description,
            status=new_task.status,
            user_id=new_task.user_id,
            created_at=new_task.created_at.isoformat(),
            updated_at=new_task.updated_at.isoformat()
        )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: int = Depends(get_current_user_id)
):
    """Update a task."""
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update fields if provided
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.status is not None:
            task.status = task_data.status

        session.add(task)
        session.commit()
        session.refresh(task)

        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            user_id=task.user_id,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a task."""
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        session.delete(task)
        session.commit()

        return None
