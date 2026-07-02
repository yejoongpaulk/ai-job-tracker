# job_app/dependency.py
import os
from fastapi import Request, HTTPException, status
from valkey import asyncio as valkey  # type: ignore[reportMissingImports]

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

# ==========================================
# CURRENT USER: returns the current user in the session.
# ==========================================
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


# ==========================================
# EXTRA PROTECTION: AI Rate Limiter Dependency Guard
# ==========================================
async def rate_limit_ai_requests(request: Request):
    """
    Token Bucket Limiter: Allows a quick burst of up to 3 AI requests 
    for quick corrections, but recharges strictly at 1 request per minute.
    """
    # 1. Inspect the incoming request body payload
    try:
        body = await request.json()
        # If this is a manual entry or a status edit without an AI description block,
        # pass it through with zero token costs!
        if not body.get("raw_job_posting"):
            return 
    except Exception:
        pass  # Fall back to standard pipeline tracking if body reading fails

    # 2. Extract client network footprint context
    client_ip = request.client.host
    redis_key = f"rate_limit:ai:{client_ip}"
    
    # --- CAPACITY DESIGN RULES ---
    MAX_BURST = 3.0          # Maximum consecutive attempts allowed
    REFILL_RATE = 60.0       # Seconds needed to earn 1 token back (1 per minute)

    now = time.time()
    
    # 3. Pull tracking records out of the openSUSE Valkey cache layers
    data = await valkey_client.hmget(redis_key, ["tokens", "last_updated"])
    
    cached_tokens = data[0]
    cached_time = data[1]

    if cached_tokens is None or cached_time is None:
        tokens = MAX_BURST
        last_updated = now
    else:
        tokens = float(cached_tokens)
        last_updated = float(cached_time)

        # Token Bucket Refill Math Equation
        elapsed = now - last_updated
        refilled_tokens = elapsed / REFILL_RATE
        tokens = min(MAX_BURST, tokens + refilled_tokens)
        last_updated = now

    # 4. Request Capacity Evaluation
    if tokens < 1.0:
        time_passed = now - last_updated
        seconds_remaining = int(max(1, REFILL_RATE - time_passed))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"AI capacity exhausted. Please wait {seconds_remaining} seconds "
                f"for your token bucket to recharge before parsing another job description."
            )
        )

    # 5. Consume 1 token from the energy bar and save changes
    tokens -= 1.0
    await valkey_client.hset(redis_key, mapping={"tokens": str(tokens), "last_updated": str(last_updated)})
    await valkey_client.expire(redis_key, 180)  # Drop caching row after 3 minutes of total inactivity