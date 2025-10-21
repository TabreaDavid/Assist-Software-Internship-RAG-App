from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import User, Collection, Document, IndexedCollection
from core.auth import get_current_user
from api.dependencies import database
from api.schemas import CollectionCreate
from services.rag_functionality import chroma_client, all_collection_id

router = APIRouter(
    prefix="/collections",
    tags=["collections"]
)

@router.post("/")
def create_collection(collection_data: CollectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = Collection(
        name=collection_data.name,
        owner_id=current_user.id,
    )

    db.add(collection)
    db.commit()
    
    return {
        "id": collection.id,
        "message": "Collection created succesfully!"
    }

@router.get("/")
def get_collections(current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collections = db.query(Collection).filter(Collection.owner_id == current_user.id).all()
    return [{"id": c.id, "name": c.name, "created_at": c.created_at} for c in collections]


@router.get("/{collection_id}")
def get_collection(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.owner_id == current_user.id,
                                             Collection.id == collection_id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    documents = db.query(Document).filter(Document.collection_id == collection_id).all()

    return {
        "id": collection.id,
        "name": collection.name,
        "created_at": collection.created_at,
        "documents": [{"id": d.id, "file_name": d.file_name, "file_type": d.file_type} for d in documents]
    }

@router.delete("/{collection_id}")
def remove_collection(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                            Collection.owner_id == current_user.id).first()

    indexed_collection = db.query(IndexedCollection).filter(IndexedCollection.collection_id == collection_id).first()

    if indexed_collection:
        chroma_client.delete_collection(name=indexed_collection.chroma_collection_name)
        db.delete(indexed_collection)

    if collection_id in all_collection_id:
        del all_collection_id[collection_id]

    db.query(Document).filter(Document.collection_id == collection.id).delete()
    db.delete(collection)
    db.commit()

    return {"message": "Collection deleted successfully"}