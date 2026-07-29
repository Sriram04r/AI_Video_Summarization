import os
import bcrypt
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

# Security Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dfc863a34a8109dbe98218a562479e0be6f1947b1e428bc57d2cf0a1c6204780")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Union[str, None]:
    """Decode a JWT access token and return the subject (user_id)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None
