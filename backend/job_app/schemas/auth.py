from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    """
    Schema for new user registration with strict length limits.
    """
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class UserLogin(BaseModel):
    """
    Schema for user authentication inputs.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

class SessionData(BaseModel):
    user_id: int
    username: str

class SessionResponse(BaseModel):
    """
    Standard corporate envelope API response payload on successful authentication.
    """
    message: str = Field(default="Authentication successful")
    session_id: str