from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    collections = relationship("Collection", back_populates="owner") 

class Collection(Base):
    __tablename__ = 'collections'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="collections")
    documents = relationship("Document", back_populates="collection")
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    file_type = Column(String)
    content = Column(String)
    collection_id = Column(Integer, ForeignKey("collections.id"))
    collection = relationship("Collection", back_populates="documents")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String)
    response = Column(String)
    collection_id = Column(Integer, ForeignKey("collections.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class IndexedCollection(Base):
    __tablename__ = 'indexed_collections'
    
    collection_id = Column(Integer, ForeignKey("collections.id"), primary_key=True)
    chroma_collection_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    collection = relationship("Collection")

#TODO
class AdminSettings(Base):
    __tablename__ = 'admin_settings'
    id = Column(Integer, primary_key=True)

