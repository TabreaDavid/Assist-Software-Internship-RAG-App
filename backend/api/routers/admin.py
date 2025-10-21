from fastapi import APIRouter, HTTPException, Depends
from services.rag_functionality import get_current_model, set_custom_context, get_custom_context
from sqlalchemy.orm import Session
from api.schemas import ModelChange, CustomContextUpdate
import os
from datetime import datetime
from dotenv import load_dotenv
from api.dependencies import database
from db.models import AdminSettings

load_dotenv()

router = APIRouter(
    prefix="/admin-settings",
    tags=["admin"]
)

@router.post("/change-model")
def change_model(model_data: ModelChange, db: Session = Depends(database.get_db)):
    admin_password = os.getenv("ADMIN_PASSWORD")

    if model_data.admin_password != admin_password:
        raise HTTPException(status_code=401, detail="Unauthorized acces")

    existing_setting = db.query(AdminSettings).filter(AdminSettings.setting_key == "openai_model").first()

    if existing_setting:
        existing_setting.setting_value = model_data.model_name
        existing_setting.updated_at = datetime.utcnow()
    else:
        new_setting = AdminSettings(setting_key="openai_model", setting_value=model_data.model_name)
        db.add(new_setting)

    db.commit()

    return {"message": f"Model changed to {model_data.model_name} successfully"}

@router.get("/current-model")
def get_current_model_setting(db: Session = Depends(database.get_db)):
    current_model = get_current_model(db)
    return {"current_model": current_model}

@router.post("/set-custom-context")
def set_custom_context_endpoint(context_data: CustomContextUpdate, db: Session = Depends(database.get_db)):
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password or context_data.admin_password != admin_password:
        raise HTTPException(status_code=401, detail="Invalid admin password")

    set_custom_context(context_data.custom_context, db)
    return {"message": "Custom context updated successfully"}

@router.get("/current-custom-context")
def get_current_custom_context_setting(db: Session = Depends(database.get_db)):
    custom_context = get_custom_context(db)
    return {"custom_context": custom_context}