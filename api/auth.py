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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

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

import random
import string
from datetime import datetime, timedelta
from api.email_service import send_verification_email

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't reveal if user exists or not
        return {"message": "If that email exists, a reset code has been sent."}
        
    # Generate a random 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Save to database with 15 minute expiry
    user.reset_code = code
    user.reset_code_expiry = datetime.utcnow() + timedelta(minutes=15)
    db.commit()
    
    # Send email
    send_verification_email(user.email, code)
    
    return {"message": "If that email exists, a reset code has been sent."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    
    if not user or not user.reset_code or user.reset_code != req.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
        
    if user.reset_code_expiry and datetime.utcnow() > user.reset_code_expiry:
        raise HTTPException(status_code=400, detail="Verification code has expired")
        
    # Valid code! Hash new password
    hashed_pwd = hash_password(req.new_password)
    user.password = hashed_pwd
    user.reset_code = None
    user.reset_code_expiry = None
    
    # Add history
    history_entry = History(
        user_id=user.user_id,
        activity="Password reset successfully"
    )
    db.add(history_entry)
    db.commit()
    
    return {"message": "Password reset successfully"}
