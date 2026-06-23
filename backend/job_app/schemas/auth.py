# job_app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    """
    Schema that holds a username, email, and password for a user.
    """
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    Email and password that are taken in at login.
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Token that holds the session id for a user.
    """
    message: str
    session_id: str
