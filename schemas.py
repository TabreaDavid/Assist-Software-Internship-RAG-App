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

class DocumentResponse(BaseModel):
    id: int
    name: str
    file_type: str
    upload_date: str

#TODO - the rest of the needed schemas