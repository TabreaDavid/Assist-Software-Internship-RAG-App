from fastapi import Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from models import Document, IndexedCollection, AdminSettings
import os, chromadb
from database import Database
from datetime import datetime
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document as LDocument, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.text_splitter import SentenceSplitter

load_dotenv()
embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
chroma_path = os.getenv("CHROMA_PATH")
database = Database()

def get_current_model(db: Session = Depends(database.get_db)):
    model_setting = db.query(AdminSettings).filter(AdminSettings.setting_key == "openai_model").first()
    return model_setting.setting_value

def get_llm_instance(db: Session):
    current_model = get_current_model(db)
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model=current_model)

def get_custom_context(db: Session = database.get_db):
    context_setting = db.query(AdminSettings).filter(AdminSettings.setting_key == "custom_context").first()
    if context_setting:
        return context_setting.setting_value
    return None

def set_custom_context(custom_context: str, db: Session = Depends(database.get_db)):
    context_setting = db.query(AdminSettings).filter(AdminSettings.setting_key == "custom_context").first()
    if context_setting:
        context_setting.setting_value = custom_context
        context_setting.updated_at = datetime.utcnow()
    else:
        context_setting = AdminSettings(setting_key="custom_context", setting_value=custom_context)
        db.add(context_setting)
    db.commit()
    return context_setting
    
chroma_client = chromadb.PersistentClient(path=chroma_path)
all_collection_id = {}

def index_document(document: Document, db: Session =database.get_db):
    collection_id = document.collection_id
    
    text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=70)
    text_chunks = text_splitter.split_text(document.content)
    
    llama_documents = []
    for i, chunk in enumerate(text_chunks):
        metadata = {"document_id": document.id, "chunk_index": i, "collection_id": collection_id}
        llama_documents.append(LDocument(text=chunk, metadata=metadata))
    
    if collection_id not in all_collection_id:
        indexed_collection = db.query(IndexedCollection).filter(IndexedCollection.collection_id == collection_id).first()
        
        if indexed_collection:
            chroma_collection = chroma_client.get_collection(name=indexed_collection.chroma_collection_name)
        else:
            chroma_collection_name = f"collection_{collection_id}"
            chroma_collection = chroma_client.get_or_create_collection(name=chroma_collection_name)
            indexed_collection = IndexedCollection(collection_id=collection_id, chroma_collection_name=chroma_collection_name)
            db.add(indexed_collection)
            db.commit()
            
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        all_collection_id[collection_id] = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

    for llama_document in llama_documents:
        all_collection_id[collection_id].insert(llama_document)

def load_indexed_collections(db: Session = Depends(database.get_db)):
    indexed_collections = db.query(IndexedCollection).all()
    
    for indexed_collection in indexed_collections:
        collection_id = indexed_collection.collection_id
        if collection_id not in all_collection_id:
            chroma_collection = chroma_client.get_collection(name=indexed_collection.chroma_collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            all_collection_id[collection_id] = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

def query_collection_index(query: str, collection_id: int, db: Session, context: list = None):
    if collection_id not in all_collection_id:
        return {"response": "No documents found in this collection", "sources": []}
    
    llm = get_llm_instance(db)
    query_engine = all_collection_id[collection_id].as_query_engine(llm=llm)
    
    custom_context = get_custom_context(db)
    
    if context:
        context_str = "\n".join(context)
        enhanced_query = f"Previous conversation context:\n{context_str}\nCurrent question: {query}"
    elif custom_context:
        enhanced_query = f"Additional context: {custom_context}\nQuestion: {query}"
    else:
        enhanced_query = query
    
    response = query_engine.query(enhanced_query)
    sources = []
    if response.source_nodes:
        for source_node in response.source_nodes:

            metadata = source_node.node.metadata
            document_id = metadata.get('document_id')
            chunk_index = metadata.get('chunk_index')

            print(document_id)
            print(chunk_index)

            if document_id is None: 
                continue
                
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document_name = document.file_name
            else:
                document_name = "Unknown document"
            
            sources.append({
                "document_name": document_name,
                "chunk_id": chunk_index,
                "document_id": document_id
            })
    
    return {
        "response": str(response),
        "sources": sources
    }