from fastapi import APIRouter, Depends, HTTPException
from core.auth import get_current_user
from sqlalchemy.orm import Session
from api.schemas import Query
from services.rag_functionality import query_collection_index
from api.dependencies import database
from db.models import Collection, ChatHistory, User

router = APIRouter(
    tags=["chat"]
)

@router.post("/query/simple")
def simple_query(query_data: Query, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.id == query_data.collection_id,
                                             Collection.owner_id == current_user.id).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    result = query_collection_index(query_data.query, query_data.collection_id, db)

    return {
        "query": query_data.query,
        "response": result["response"],
        "sources": result["sources"]
    }

@router.post("/query/chat")
def chat_query(query_data: Query, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.id == query_data.collection_id,
                                             Collection.owner_id == current_user.id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    chat_history = db.query(ChatHistory).filter(ChatHistory.collection_id == query_data.collection_id,
                                                ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at).limit(10).all()

    context_messages = []
    for chat in chat_history:
        context_messages.append(f"Human: {chat.query}")
        context_messages.append(f"Assistant: {chat.response}")

    result = query_collection_index(query_data.query, query_data.collection_id, db, context=context_messages)
    response_text = result["response"]

    chat_record = ChatHistory(
        query=query_data.query,
        response=response_text,
        collection_id=query_data.collection_id,
        user_id=current_user.id)

    db.add(chat_record)
    db.commit()

    return {
        "query": query_data.query,
        "response": result["response"],
        "sources": result["sources"]
    }

@router.get("/chat-history/{collection_id}")
def get_chat_history(collection_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id,
                                             Collection.owner_id == current_user.id).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    chat_history = db.query(ChatHistory).filter(ChatHistory.collection_id == collection_id,
                                                ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at).all()
    
    return [{"query": chat.query, "response": chat.response, "created_at": chat.created_at} for chat in chat_history]