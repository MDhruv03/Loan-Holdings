"""
Authentication service for user login and session management
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Request, HTTPException
from app.config import ADMIN_USERNAME, ADMIN_PASSWORD, SESSION_COOKIE_NAME


def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_credentials(username: str, password: str) -> bool:
    """Verify login credentials"""
    return username == ADMIN_USERNAME and hash_password(password) == hash_password(ADMIN_PASSWORD)


def create_session(username: str) -> dict:
    """Create session data"""
    return {
        "username": username,
        "login_time": datetime.now().isoformat()
    }


def get_current_user(request: Request) -> Optional[str]:
    """Get current logged in user from session"""
    return request.session.get("username")


def require_auth(request: Request):
    """Dependency to require authentication"""
    username = get_current_user(request)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    return username
