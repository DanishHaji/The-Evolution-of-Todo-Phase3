"""JWT authentication middleware for Phase 3 AI Todo Chatbot."""

from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# JWT configuration
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")

JWT_ALGORITHM = "HS256"


def verify_jwt(authorization: Optional[str] = Header(None)) -> int:
    """
    Verify JWT token and extract user_id.

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        user_id: Authenticated user ID from JWT token

    Raises:
        HTTPException: 401 if token is invalid, missing, or expired
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>" format
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Expected 'Bearer'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify and decode JWT token
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing 'sub' claim",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Convert string back to integer (JWT RFC 7519 requires sub to be a string)
        try:
            user_id: int = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_jwt_token(user_id: int, expires_days: int = 7) -> str:
    """
    Create JWT token for user authentication.

    Args:
        user_id: User ID to encode in token
        expires_days: Token expiration in days (default: 7)

    Returns:
        JWT token string
    """
    from datetime import datetime, timedelta

    payload = {
        "sub": str(user_id),  # JWT RFC 7519 requires sub to be a string
        "exp": datetime.utcnow() + timedelta(days=expires_days),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    # Ensure token is string (newer PyJWT returns string by default)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


# FastAPI dependency for protected routes
def get_current_user_id(user_id: int = Depends(verify_jwt)) -> int:
    """
    FastAPI dependency to get current authenticated user ID.

    Usage:
        @app.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: int,
            authenticated_user_id: int = Depends(get_current_user_id)
        ):
            if user_id != authenticated_user_id:
                raise HTTPException(403, "User ID mismatch")
            # ... rest of endpoint logic
    """
    return user_id
