from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from db.models import User, Collection
from api.dependencies import database
from sqlalchemy.orm import Session
from services.rag_functionality import index_document, Document
from core.auth import get_current_user
import os
from services.file_processing import FileProcess

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

@router.post("/upload")
def upload_document(collection_id: int, file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):

    collection = db.query(Collection).filter(Collection.id == collection_id, Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    content = file.file.read()

    file_extension = os.path.splitext(file.filename)[1][1:]
    file_processor = FileProcess(file_extension, content)

    if file_extension in file_processor.get_extensions():
        processed_content = file_processor.process_file()
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
    index_document(document, db)

    return {"message": "Document uploaded successfully"}


@router.get("/{collection_id}")
def get_documents(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                             Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    documents = db.query(Document).filter(Document.collection_id == collection_id).all()
    return [{"content": d.content, "uploaded_at": d.uploaded_at, "file_name": d.file_name} for d in documents]