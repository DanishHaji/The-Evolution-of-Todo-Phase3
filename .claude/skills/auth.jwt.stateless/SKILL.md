---
name: auth.jwt.stateless
description: "Implement stateless JWT authentication for the chat API, ensuring secure user identification without server-side session storage. Use when protecting chat endpoints, verifying user identity in stateless architecture, implementing JWT middleware for FastAPI, or token refresh logic."
category: Authentication / Security
complexity: Medium
phase: 3
dependencies: ["PyJWT", "FastAPI", "python-jose"]
---

# Skill: JWT Stateless Authentication

**Category**: Authentication / Security
**Complexity**: Medium
**Phase**: 3 (AI-Powered Chatbot)
**Dependencies**: PyJWT, FastAPI

## Purpose

Implement stateless JWT authentication for the chat API, ensuring secure user identification without server-side session storage.

## When to Use

- Protecting chat endpoints
- Verifying user identity in stateless architecture
- Implementing JWT middleware for FastAPI
- Token refresh logic

## Pattern

### 1. JWT Configuration

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT Configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Token Generation

```python
# backend/app/auth/jwt.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional, Dict

def create_access_token(user_id: str) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User identifier

    Returns:
        Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access"
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token

def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token.

    Args:
        user_id: User identifier

    Returns:
        Encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh"
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return token

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """
    Verify JWT token and extract user_id.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        User ID if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != token_type:
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        return user_id

    except JWTError:
        return None
```

### 3. Authentication Dependency

```python
# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt import verify_token
from typing import Dict

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, str]:
    """
    Dependency to get current authenticated user.

    Extracts JWT from Authorization header and verifies it.

    Returns:
        Dict with user_id

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials

    user_id = verify_token(token, token_type="access")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"user_id": user_id}

async def verify_user_access(
    user_id: str,
    current_user: Dict = Depends(get_current_user)
) -> None:
    """
    Verify that authenticated user matches requested user_id.

    Args:
        user_id: Requested user ID from path parameter
        current_user: Authenticated user from token

    Raises:
        HTTPException: If user doesn't have access
    """
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
```

### 4. Protected Chat Endpoint

```python
# backend/app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, verify_user_access

router = APIRouter()

@router.post("/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: Dict = Depends(get_current_user),
    _: None = Depends(verify_user_access)
):
    """
    Stateless chat endpoint with JWT authentication.

    - Token verified via get_current_user dependency
    - User authorization checked via verify_user_access
    - No server-side session storage
    """
    # User is authenticated and authorized at this point
    # Proceed with chat logic...

    return {"message": "Chat processed"}
```

### 5. Token Refresh Endpoint

```python
# backend/app/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from app.auth.jwt import verify_token, create_access_token, create_refresh_token
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(credentials = Depends(security)):
    """
    Refresh access token using refresh token.

    Returns new access token and rotated refresh token.
    """
    refresh_token = credentials.credentials

    # Verify refresh token
    user_id = verify_token(refresh_token, token_type="refresh")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Generate new tokens
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)  # Token rotation

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
```

## Acceptance Criteria

- [ ] JWT tokens include user_id and expiration
- [ ] Access tokens expire after 15 minutes
- [ ] Refresh tokens expire after 7 days
- [ ] Token verification rejects invalid/expired tokens
- [ ] Protected endpoints require valid JWT
- [ ] User can only access their own resources
- [ ] Refresh token rotation implemented
- [ ] No server-side session storage (fully stateless)

## Frontend Integration

```typescript
// frontend/lib/auth.ts
export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('refresh_token');

  if (!refreshToken) {
    return null;
  }

  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    });

    if (!response.ok) {
      // Refresh token expired, logout user
      localStorage.clear();
      window.location.href = '/login';
      return null;
    }

    const data = await response.json();

    // Store new tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    return data.access_token;
  } catch (error) {
    console.error('Token refresh failed:', error);
    return null;
  }
}

// Axios interceptor for automatic token refresh
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const newToken = await refreshAccessToken();

      if (newToken) {
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);
```

## Security Best Practices

1. **Token Storage**:
   - Access token: localStorage (short-lived)
   - Refresh token: httpOnly cookie (more secure) or localStorage

2. **Token Expiration**:
   - Short access token lifetime (15 min)
   - Longer refresh token lifetime (7 days)
   - Automatic token refresh on expiration

3. **Secret Management**:
   - Use strong, random JWT_SECRET (min 32 characters)
   - Store in environment variables, never commit
   - Rotate secrets periodically

4. **CORS Configuration**:
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=[os.getenv("FRONTEND_URL")],  # Never use "*"
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Testing

```python
# test_jwt_auth.py
import pytest
from app.auth.jwt import create_access_token, verify_token
from datetime import timedelta
from jose import jwt
from app.config import settings

def test_create_access_token():
    token = create_access_token("test-user")
    assert token is not None
    assert isinstance(token, str)

def test_verify_valid_token():
    token = create_access_token("test-user")
    user_id = verify_token(token)
    assert user_id == "test-user"

def test_verify_expired_token():
    # Create expired token
    payload = {
        "sub": "test-user",
        "exp": datetime.utcnow() - timedelta(minutes=1),
        "type": "access"
    }
    token = jwt.encode(payload, settings.JWT_SECRET, settings.JWT_ALGORITHM)

    user_id = verify_token(token)
    assert user_id is None

def test_verify_wrong_secret():
    token = jwt.encode(
        {"sub": "test-user", "type": "access"},
        "wrong-secret",
        settings.JWT_ALGORITHM
    )

    user_id = verify_token(token)
    assert user_id is None
```

## Common Issues

1. **401 Unauthorized**: Token expired or invalid
   - Solution: Implement automatic token refresh

2. **403 Forbidden**: User accessing wrong resource
   - Solution: Verify user_id matches in path and token

3. **Token not found**: Missing Authorization header
   - Solution: Ensure frontend attaches token to requests

4. **CORS errors**: Frontend can't access API
   - Solution: Configure CORS with correct frontend URL

## Performance

- JWT verification is fast (cryptographic signature check)
- No database lookup required for authentication
- Fully stateless (horizontally scalable)
- Use token caching for repeated verification (optional)

## References

- [JWT.io](https://jwt.io/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- Phase 3 Spec: `specs/phase3/authentication.md`
- Related Skills: `auth.better.integration.md`

## Version

1.0.0 - Initial Phase 3 implementation
