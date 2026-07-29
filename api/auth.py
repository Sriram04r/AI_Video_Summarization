from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database.schema import User, History
from backend.database_utils import get_db
from backend.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login-oauth2")

# Pydantic Schemas
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: str

class UserProfile(BaseModel):
    user_id: int
    username: str
    email: str

# Dependency to get current user from JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserProfile:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserProfile(user_id=user.user_id, username=user.username, email=user.email)


@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Hash password and save user
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Add activity history
    history_entry = History(
        user_id=new_user.user_id,
        activity=f"User registered with username: {new_user.username}"
    )
    db.add(history_entry)
    db.commit()
    
    # Generate token
    token = create_access_token(subject=new_user.user_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=new_user.username,
        email=new_user.email
    )


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Add activity history
    history_entry = History(
        user_id=user.user_id,
        activity="User logged in"
    )
    db.add(history_entry)
    db.commit()
    
    # Generate token
    token = create_access_token(subject=user.user_id)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        email=user.email
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: UserProfile = Depends(get_current_user)):
    return current_user
