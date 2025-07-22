from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from schemas import UserCreate, UserLogin, CollectionCreate
from database import get_db, create_tables
from models import User, Collection, Document, ChatHistory, AdminSettings
from auth import hash_password, create_access_token, verify_password, get_current_user
import os
from file_processing import process_csv, process_pdf, process_txt, process_xml

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
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(user)
    db.commit()

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
def update_profile(new_email: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.email = new_email
    db.commit()
    return {"message": "Profile updated successfully"}


@app.post("/collections")
def create_collection(collection_data: CollectionCreate, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    collection = Collection(
        name=collection_data.name,
        owner_id=current_user.id,
        owner=current_user
    )
    db.add(collection)
    db.commit()
    return {"id": collection.id,
            "message": "Collection created successfully"}


@app.get("/collections/")
def get_collections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collections = db.query(Collection).filter(Collection.owner_id == current_user.id).all()

    result = []
    for c in collections:
        result.append({
            "id": c.id,
            "name": c.name,
            "created_at": c.created_at
        })

    return result


@app.get("/collections/{collection_id}")
def get_collection(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.owner_id == current_user.id,
                                             Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    documents = db.query(Document).filter(Document.collection_id == collection_id).all()
    result = []

    for d in documents:
        result.append({
            "id": d.id,
            "file_name": d.file_name,
            "file_type": d.file_type
        })

    return {
        "id": collection.id,
        "name": collection.name,
        "created_at": collection.created_at,
        "documents": result
    }


@app.delete("/collections/{collection_id}")
def remove_collection(collection_id: int, current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                             Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    db.query(Document).filter(Document.collection_id == collection.id).delete()
    db.delete(collection)
    db.commit()

    return {"message": "Collection deleted successfully"}


@app.post("/documents/upload")
def upload_document(collection_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                             Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    content = file.file.read()

    file_extension = os.path.splitext(file.filename)[1][1:]

    if file_extension == "txt":
        processed_content = process_txt(content)

    elif file_extension == "pdf":
        processed_content = process_pdf(content)

    elif file_extension == "xml":
        processed_content = process_xml(content)

    elif file_extension == "csv":
        processed_content = process_csv(content)

    else:
        raise HTTPException(status_code=400, detail="File type not supported")

    document = Document(
        file_name=file.filename,
        file_type=file_extension,
        content=processed_content,
        collection_id=collection_id
    )

    db.add(document)
    db.commit()

    return {"message": "Document uploaded successfully"}


@app.get("/documents/{collection_id}")
def get_documents(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                             Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    documents = db.query(Document).filter(Document.collection_id == collection_id).all()
    return [{"content": d.content} for d in documents]


@app.get("/")
def root():
    return {"App": "Is running"}