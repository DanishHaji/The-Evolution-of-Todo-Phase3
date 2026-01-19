"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.models import User, engine
from app.auth import create_jwt_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    token: str
    user: dict


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user."""
    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = pwd_context.hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Create JWT token
        token = create_jwt_token(new_user.id)

        return TokenResponse(
            token=token,
            user={"id": str(new_user.id), "email": new_user.email}
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user and return JWT token."""
    with Session(engine) as session:
        # Find user by email
        statement = select(User).where(User.email == credentials.email)
        user = session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not pwd_context.verify(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create JWT token
        token = create_jwt_token(user.id)

        return TokenResponse(
            token=token,
            user={"id": str(user.id), "email": user.email}
        )
