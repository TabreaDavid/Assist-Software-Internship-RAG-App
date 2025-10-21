from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import UserCreate, UserLogin
from db.models import User
from api.dependencies import database
from core.auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["auth"])

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(User).filter(user_data.name == User.name).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = hash_password(user_data.password)

    user = User(
        name=user_data.name,
        password_hash=hashed_password,
        email=user_data.email
    )

    db.add(user)
    db.commit()

    return {"Message": "User created succesfully"}

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(User).filter(User.name == user_data.name).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.id)

    return {"token": token}
