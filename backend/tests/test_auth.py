"""Unit tests for JWT authentication (TDD)."""

import pytest
from fastapi import HTTPException
from app.auth import verify_jwt, create_jwt_token
import jwt
from datetime import datetime, timedelta
import os


def test_create_jwt_token(mock_user_id, mock_jwt_secret):
    """Test JWT token creation with valid user_id."""
    token = create_jwt_token(mock_user_id)

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = jwt.decode(token, mock_jwt_secret, algorithms=["HS256"])
    assert payload["sub"] == str(mock_user_id)  # JWT RFC 7519 requires sub to be a string
    assert "exp" in payload
    assert "iat" in payload


def test_verify_jwt_valid_token(mock_jwt_token, mock_jwt_secret, mock_user_id):
    """Test JWT verification with valid token."""
    authorization = f"Bearer {mock_jwt_token}"
    user_id = verify_jwt(authorization)

    assert user_id == mock_user_id


def test_verify_jwt_missing_authorization():
    """Test JWT verification fails when authorization header is missing."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt(None)

    assert exc_info.value.status_code == 401
    assert "Authorization header missing" in exc_info.value.detail


def test_verify_jwt_invalid_scheme():
    """Test JWT verification fails with non-Bearer scheme."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt("Basic some_token_here")

    assert exc_info.value.status_code == 401
    assert "Invalid authentication scheme" in exc_info.value.detail


def test_verify_jwt_malformed_header():
    """Test JWT verification fails with malformed header."""
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt("InvalidHeaderFormat")

    assert exc_info.value.status_code == 401
    assert "Invalid authorization header format" in exc_info.value.detail


def test_verify_jwt_expired_token(expired_jwt_token, mock_jwt_secret):
    """Test JWT verification fails with expired token."""
    authorization = f"Bearer {expired_jwt_token}"

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt(authorization)

    assert exc_info.value.status_code == 401
    assert "Token has expired" in exc_info.value.detail


def test_verify_jwt_invalid_signature(mock_user_id, mock_jwt_secret):
    """Test JWT verification fails with wrong secret."""
    # Create token with one secret
    token = jwt.encode(
        {
            "sub": str(mock_user_id),  # JWT RFC 7519 requires sub to be a string
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        },
        "wrong_secret",
        algorithm="HS256",
    )

    # Try to verify with different secret (mock_jwt_secret from fixture)
    authorization = f"Bearer {token}"

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt(authorization)

    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail


def test_verify_jwt_missing_sub_claim(mock_jwt_secret):
    """Test JWT verification fails when sub claim is missing."""
    # Create token without 'sub' claim
    token = jwt.encode(
        {
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        },
        mock_jwt_secret,
        algorithm="HS256",
    )

    authorization = f"Bearer {token}"

    with pytest.raises(HTTPException) as exc_info:
        verify_jwt(authorization)

    assert exc_info.value.status_code == 401
    assert "Token payload missing 'sub' claim" in exc_info.value.detail


def test_jwt_token_expiration_days(mock_jwt_secret):
    """Test JWT token expiration can be customized."""
    # Create token with custom expiration
    token = create_jwt_token(user_id=1, expires_days=1)

    payload = jwt.decode(token, mock_jwt_secret, algorithms=["HS256"])

    # Check expiration is approximately 1 day from now
    exp_datetime = datetime.utcfromtimestamp(payload["exp"])  # Use UTC
    expected_exp = datetime.utcnow() + timedelta(days=1)

    # Allow 5 second tolerance for test execution time
    assert abs((exp_datetime - expected_exp).total_seconds()) < 5
