# job_app/routers/auth.py
import uuid
import bcrypt
import valkey
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Explicit relative imports from your folder tree
from ..database import get_db
from ..models.user import User
from ..schemas.auth import UserRegister, UserLogin, TokenResponse

# Connect to Valkey (Configure server details via config.py if needed)
valkey_client = valkey.Valkey(host='[FILL IN WITH .ENV SUBS]', port=-1, decode_responses=True)

auth_router = APIRouter(
    prefix="/users",
    tags=["Users/Auth"]
)

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}


@auth_router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    password_match = bcrypt.checkpw(
        login_data.password.encode('utf-8'), 
        user.hashed_password.encode('utf-8')
    )
    if not password_match:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Session tracking inside Valkey
    session_id = str(uuid.uuid4())
    valkey_client.setex(f"session:{session_id}", 86400, str(user.id))
    
    return {"message": "Logged in successfully", "session_id": session_id}
