from fastapi import FastAPI
from dotenv import load_dotenv
import os
from services.rag_functionality import load_indexed_collections
from db.models import AdminSettings
from api.dependencies import database
from api.routers import authentication, user, collections, documents, chat, admin

load_dotenv()
app = FastAPI()
database.create_tables()

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(collections.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(admin.router)


db = database.db_session()
try:
    load_indexed_collections(db)
    existing_model_setting = db.query(AdminSettings).filter(AdminSettings.setting_key == "openai_model").first()
    if not existing_model_setting:
        default_model = AdminSettings(setting_key="openai_model",setting_value=os.getenv("OPENAI_MODEL"))
        db.add(default_model)
        db.commit()
finally:
    db.close()


@app.get("/")
def root():
    return {"App": "Is running"}
