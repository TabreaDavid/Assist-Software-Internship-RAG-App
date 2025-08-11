from passlib.context import CryptContext
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_db
from models import User
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(hashed_password: str, password: str):
    return pwd_context.verify(password, hashed_password)

def create_access_token(username: str, id: int):
    payload = {
        "user_id": id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except Exception as e:
        print(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
        