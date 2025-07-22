from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from schemas import UserCreate, UserLogin
from database import get_db, create_tables
from models import User
from auth import hash_password, create_access_token, verify_password, get_current_user
import os

load_dotenv()

app = FastAPI()
create_tables()

@app.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.name == user_data.name).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_password = hash_password(user_data.password)
    user = User(
        name = user_data.name,
        email = user_data.email,
        password_hash = hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"Message": "User created succesfully"}
    


@app.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == user_data.name).first()

    if not user or not verify_password(user.password_hash, user_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.name, user.id)
    return {"token": token}

@app.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at
    }


@app.put("/profile")
def update_profile():
    pass

@app.post("/collections")
def create_collection():
    pass

@app.get("/collections")
def get_collection():
    pass

@app.delete("/collections")
def remove_collection():
    pass

@app.get("/")
def root():
    return {"App": "Is running"}