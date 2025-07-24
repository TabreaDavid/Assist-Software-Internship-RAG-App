from fastapi import Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import get_db
from models import Document, IndexedCollection
import os, chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document as LDocument, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI


load_dotenv()
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = OpenAI(api_key=os.getenv("OPEN_API_KEY"), model=os.getenv("OPENAI_MODEL"))
    
chroma_client = chromadb.PersistentClient(path="./chroma_db")
all_collection_id = {}

def index_document(document: Document, db: Session = Depends(get_db)):
    llama_document = LDocument(text=document.content)
    collection_id = document.collection_id

    if collection_id not in all_collection_id:
        indexed_collection = db.query(IndexedCollection).filter(IndexedCollection.collection_id == collection_id).first()
        
        if indexed_collection:
            chroma_collection = chroma_client.get_collection(name=indexed_collection.chroma_collection_name)
        else:
            chroma_collection_name = f"collection_{collection_id}"
            chroma_collection = chroma_client.create_collection(name=chroma_collection_name)
            indexed_collection = IndexedCollection(collection_id=collection_id, chroma_collection_name=chroma_collection_name)
            db.add(indexed_collection)
            db.commit()
            
        
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        all_collection_id[collection_id] = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

    all_collection_id[collection_id].insert(llama_document)

def load_indexed_collections(db: Session = Depends(get_db)):
    indexed_collections = db.query(IndexedCollection).all()
    
    for indexed_collection in indexed_collections:
        collection_id = indexed_collection.collection_id
        if collection_id not in all_collection_id:
            chroma_collection = chroma_client.get_collection(name=indexed_collection.chroma_collection_name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            all_collection_id[collection_id] = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

def query_collection_index(query: str, collection_id: int, context: list = None):
    if collection_id not in all_collection_id:
        return "No documents found in this collection"
    
    query_engine = all_collection_id[collection_id].as_query_engine(llm=llm)
    
    if context:
        context_str = "\n".join(context)
        enhanced_query = f"Previous conversation context:\n{context_str}\n\nCurrent question: {query}"
        return str(query_engine.query(enhanced_query))
    else:
        return str(query_engine.query(query))
    

