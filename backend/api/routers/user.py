from fastapi import APIRouter, Depends
from core.auth import get_current_user
from db.models import User
from sqlalchemy.orm import Session
from api.dependencies import database

router = APIRouter(
    prefix="/profile",
    tags=["user"]
)

@router.get("/")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@router.put("/")
def update_profile(new_email: str, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    current_user.email = new_email
    db.commit()
    return {"message": "Profile updated sucessfully"}