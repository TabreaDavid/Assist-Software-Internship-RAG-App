from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from dotenv import load_dotenv
import os

load_dotenv()

# DB SETUP
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
DB_Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    collections = relationship("Collection",
                               back_populates="owner")  # string with the name of the attribute in the other class


class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="collections")
    documents = relationship("Document", back_populates="collection")


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    file_type = Column(String)
    content = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    collection_id = Column(Integer, ForeignKey("collections.id"))
    collection = relationship("Collection", back_populates="documents")


class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(String)
    answer = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)


# TODO
class AdminSettings(Base):
    __tablename__ = 'admin_settings'
    id = Column(Integer, primary_key=True)


def get_db():
    db = DB_Session()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

app = FastAPI()


# TODO
@app.post("/register")
def register():
    pass


@app.post("/login")
def login():
    pass


@app.get("/profile")
def get_profile():
    pass


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