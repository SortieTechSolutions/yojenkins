"""FastAPI dependency injection for per-user YoJenkins instances."""

import time
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from yojenkins.yo_jenkins.yojenkins import YoJenkins

SECRET_KEY = "yojenkins-webapp-secret-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600
SESSION_TTL_SECONDS = 1800

security = HTTPBearer()

# In-memory session store: user_id -> (YoJenkins instance, last_access_time)
_sessions: dict[str, tuple[YoJenkins, float]] = {}


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for the given user session."""
    payload = {
        "sub": user_id,
        "exp": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def store_session(user_id: str, yj: YoJenkins) -> None:
    """Store a YoJenkins instance for the given user session."""
    _sessions[user_id] = (yj, time.time())


def _decode_token(token: str) -> Optional[str]:
    """Decode JWT and return the user_id (subject), or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def cleanup_expired_sessions() -> None:
    """Remove sessions that haven't been accessed within the TTL."""
    now = time.time()
    expired = [uid for uid, (_, last) in _sessions.items() if now - last > SESSION_TTL_SECONDS]
    for uid in expired:
        del _sessions[uid]


async def get_yo_jenkins(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> YoJenkins:
    """FastAPI dependency that returns the authenticated YoJenkins for the current user."""
    user_id = _decode_token(credentials.credentials)
    if not user_id or user_id not in _sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid token. Please login again.",
        )
    yj, _ = _sessions[user_id]
    _sessions[user_id] = (yj, time.time())
    return yj
