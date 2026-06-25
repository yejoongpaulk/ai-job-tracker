import secrets
import bcrypt
from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database import get_db
from ..models.user import User
from ..dependency import valkey_client, COOKIE_NAME, get_current_user
from ..schemas.auth import UserRegister, UserLogin, SessionData, SessionResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==========================================
# 1. Password Hashing Helpers (Synchronous but brief)
# ==========================================
def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ==========================================
# 2. Registration Endpoint
# ==========================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user, ensuring email and username are unique.
    """
    # Check if username or email already exists concurrently
    query = select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered."
        )
    
    # Hash password and create database model instance
    hashed = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed
    )
    
    db.add(new_user)
    await db.commit()
    return {"detail": "User registered successfully."}


# ==========================================
# 3. Login Endpoint
# ==========================================
@router.post("/login", response_model=SessionResponse)
async def login(login_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a user, spins up a secure session token, and drops an HTTP-Only cookie.
    """
    # Fetch user by unique email using modern SQLAlchemy syntax
    query = select(User).where(User.email == login_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # Secure practice: use generic error details to mitigate timing/enumeration attacks
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
        
    # Generate an unguessable token string
    session_token = secrets.token_urlsafe(32)
    
    # Bind user context payload to the session object
    session_payload = SessionData(user_id=user.id, username=user.username)
    
    # Store stringified session in Valkey memory with a 14-day expiration (1209600 seconds)
    await valkey_client.setex(
        name=f"session:{session_token}",
        time=1209600,
        value=session_payload.model_dump_json()
    )
    
    # Drop the security-focused cookie directly onto the response pipeline
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=1209600,
    )
    
    return SessionResponse(message="Authentication successful.", session_id=session_token)


# ==========================================
# 4. Logout Endpoint
# ==========================================
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: SessionData = Depends(get_current_user)
):
    """
    Invalidates a user's active token inside Valkey storage and removes the client cookie.
    """
    # Read the token right from the request object cookies context
    session_id = request.cookies.get(COOKIE_NAME)
    
    if session_id:
        # Wipe trace of active session authorization out of Valkey cache
        await valkey_client.delete(f"session:{session_id}")
        
    # Overwrite browser storage cookie pointer immediately
    response.delete_cookie(key=COOKIE_NAME)
    return {"detail": "Successfully logged out."}


# ==========================================
# 5. Get Current User Profile Endpoint
# ==========================================
@router.get("/me", response_model=SessionData)
async def get_me(current_user: SessionData = Depends(get_current_user)) -> SessionData:
    """
    Returns the active user context payload if their Valkey session cookie is valid.
    This is what the front-end hits on boot to verify the user is logged in.
    """
    return current_user