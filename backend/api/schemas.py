from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    name: str
    password: str

class CollectionCreate(BaseModel):
    name: str

class Query(BaseModel):
    query: str
    collection_id: int

class ModelChange(BaseModel):
    admin_password: str
    model_name: str

class CustomContextUpdate(BaseModel):
    admin_password: str
    custom_context: str

class SourceInfo(BaseModel):
    document_name: str
    chunk_id: Optional[int]
    document_id: int

class QueryResponse(BaseModel):
    query: str
    response: str
    sources: List[SourceInfo]