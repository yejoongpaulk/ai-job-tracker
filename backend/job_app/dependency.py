# job_app/dependency.py
import os
from fastapi import Request, HTTPException, status
from valkey import asyncio as valkey  # type: ignore[reportMissingImports]

# Import get_db directly from your database file!
from .database import get_db
from .schemas.auth import SessionData

import os

try:
    VALKEY_URL = os.environ["VALKEY_URL"]
except KeyError:
    raise RuntimeError(
        "CRITICAL STARTUP ERROR: The 'VALKEY_URL' environment variable is not set. " +
        "Please configure your environment or .env file before launching."
    ) from None


valkey_client = valkey.from_url(VALKEY_URL, decode_responses=True)

COOKIE_NAME = "job_tracker_session"

async def get_current_user(request: Request) -> SessionData:
    """
    Reads the session cookie, checks Valkey, and returns the validated user data.
    """
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Missing session cookie.",
        )
    
    session_json = await valkey_client.get(f"session:{session_id}")
    if not session_json:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated: Session has expired or is invalid.",
        )
    
    return SessionData.model_validate_json(session_json)
