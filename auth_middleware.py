"""
Authentication Middleware for StarCy Backend
Provides JWT-based authentication and rate limiting
"""

import os
import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collections import defaultdict

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_THIS_IN_PRODUCTION")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Rate limiting storage (in-memory for now, will move to Redis/DB later)
rate_limit_storage: Dict[str, list] = defaultdict(list)

# Security scheme
security = HTTPBearer()


class RateLimitExceeded(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )


class User:
    """User model for authenticated requests"""
    def __init__(self, user_id: str, email: Optional[str] = None):
        self.user_id = user_id
        self.email = email


def create_access_token(user_id: str, email: Optional[str] = None) -> str:
    """
    Create a JWT access token for a user
    
    Args:
        user_id: Unique user identifier
        email: Optional user email
    
    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired. Please authenticate again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token from request header
    
    Returns:
        User object with user_id and email
    
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload."
        )
    
    return User(
        user_id=user_id,
        email=payload.get("email")
    )


def check_rate_limit(user_id: str, max_requests: int = 10, window_seconds: int = 60):
    """
    Check if user has exceeded rate limit
    
    Args:
        user_id: User identifier
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    
    Raises:
        RateLimitExceeded: If rate limit is exceeded
    """
    now = time.time()
    window_start = now - window_seconds
    
    # Get user's request history
    requests = rate_limit_storage[user_id]
    
    # Remove old requests outside the window
    requests = [req_time for req_time in requests if req_time > window_start]
    rate_limit_storage[user_id] = requests
    
    # Check if limit exceeded
    if len(requests) >= max_requests:
        raise RateLimitExceeded()
    
    # Add current request
    requests.append(now)


async def rate_limited_user(
    user: User = Depends(get_current_user),
    max_requests: int = 10,
    window_seconds: int = 60
) -> User:
    """
    Dependency that combines authentication and rate limiting
    
    Args:
        user: Authenticated user from get_current_user
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
    
    Returns:
        User object if authentication and rate limit checks pass
    
    Raises:
        HTTPException: If authentication fails
        RateLimitExceeded: If rate limit is exceeded
    """
    check_rate_limit(user.user_id, max_requests, window_seconds)
    return user


def validate_device_token(device_token: str, user: User) -> bool:
    """
    Validate that a device token belongs to the authenticated user
    
    Args:
        device_token: Device token to validate
        user: Authenticated user
    
    Returns:
        True if device belongs to user
    
    Note:
        This is a placeholder. In production, check against database.
    """
    # TODO: Implement actual device ownership validation
    # For now, we'll trust the user_id in the token
    return True


# Optional: API Key authentication for server-to-server communication
def verify_api_key(api_key: str) -> bool:
    """
    Verify an API key for server-to-server authentication
    
    Args:
        api_key: API key to verify
    
    Returns:
        True if API key is valid
    """
    valid_api_keys = os.getenv("API_KEYS", "").split(",")
    return api_key in valid_api_keys and api_key != ""


async def get_api_key_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """
    Dependency for API key authentication
    
    Args:
        credentials: HTTP Bearer token (API key)
    
    Returns:
        User object for API key
    
    Raises:
        HTTPException: If API key is invalid
    """
    api_key = credentials.credentials
    
    if not verify_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key."
        )
    
    return User(user_id="api_key_user", email=None)
