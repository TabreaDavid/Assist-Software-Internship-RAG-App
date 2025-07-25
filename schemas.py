from pydantic import BaseModel

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
    custom_context: str = None

class ModelChange(BaseModel):
    admin_password: str
    model_name: str