# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/dbname")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class DataChunk(Base):
    __tablename__ = "data_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chunk_id = Column(Integer, nullable=False,unique = True)
    source_file = Column(String(500), nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    start_unit = Column(Integer, nullable=False)
    end_unit = Column(Integer, nullable=False)
    embedding_model = Column(String(100), nullable=False)
    embedding = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class DataChunkBase(BaseModel):
    chunk_id: int
    source_file: str = Field(..., max_length=500)
    chunk_text: str
    token_count: int
    start_unit: int
    end_unit: int
    embedding_model: str = Field(..., max_length=100)
    embedding: str = Field(..., max_length=1000)

class DataChunkCreate(DataChunkBase):
    pass

class DataChunkUpdate(BaseModel):
    chunk_id: Optional[int] = None
    source_file: Optional[str] = Field(None, max_length=500)
    chunk_text: Optional[str] = None
    token_count: Optional[int] = None
    start_unit: Optional[int] = None
    end_unit: Optional[int] = None
    embedding_model: Optional[str] = Field(None, max_length=100)
    embedding: Optional[str] = Field(None, max_length=1000)

class DataChunkResponse(DataChunkBase):
    id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(
    title="Data Chunks API",
    description="CRUD API for managing data chunks with embeddings",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD Operations
def create_data_chunk(db: Session, chunk_data: DataChunkCreate):
    db_chunk = DataChunk(**chunk_data.dict())
    db.add(db_chunk)
    db.commit()
    db.refresh(db_chunk)
    return db_chunk

def get_data_chunk(db: Session, chunk_id: uuid.UUID):
    return db.query(DataChunk).filter(DataChunk.id == chunk_id).first()

def get_data_chunks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DataChunk).offset(skip).limit(limit).all()

def update_data_chunk(db: Session, chunk_id: uuid.UUID, chunk_update: DataChunkUpdate):
    db_chunk = db.query(DataChunk).filter(DataChunk.id == chunk_id).first()
    if db_chunk:
        update_data = chunk_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_chunk, key, value)
        db.commit()
        db.refresh(db_chunk)
    return db_chunk

def delete_data_chunk(db: Session, chunk_id: uuid.UUID):
    db_chunk = db.query(DataChunk).filter(DataChunk.id == chunk_id).first()
    if db_chunk:
        db.delete(db_chunk)
        db.commit()
    return db_chunk

# Additional Pydantic Models for specific responses
class ChunkTextResponse(BaseModel):
    id: uuid.UUID
    chunk_text: str
    
    class Config:
        from_attributes = True

# Additional CRUD function for chunk text only
def get_chunk_texts_only(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DataChunk.id, DataChunk.chunk_text).offset(skip).limit(limit).all()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Data Chunks API is running"}

@app.post("/chunks/", response_model=DataChunkResponse)
async def create_chunk(chunk: DataChunkCreate, db: Session = Depends(get_db)):
    """Create a new data chunk"""
    try:
        return create_data_chunk(db=db, chunk_data=chunk)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chunks/texts", response_model=List[ChunkTextResponse])
async def get_chunk_texts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get only chunk_text column from all data chunks"""
    chunk_texts = get_chunk_texts_only(db, skip=skip, limit=limit)
    return [{"id": chunk.id, "chunk_text": chunk.chunk_text} for chunk in chunk_texts]

@app.get("/chunks/", response_model=List[DataChunkResponse])
async def get_chunks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all data chunks with pagination"""
    chunks = get_data_chunks(db, skip=skip, limit=limit)
    return chunks

@app.get("/chunks/{chunk_id}", response_model=DataChunkResponse)
async def get_chunk(chunk_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get a specific data chunk by ID"""
    db_chunk = get_data_chunk(db, chunk_id=chunk_id)
    if db_chunk is None:
        raise HTTPException(status_code=404, detail="Data chunk not found")
    return db_chunk

@app.put("/chunks/{chunk_id}", response_model=DataChunkResponse)
async def update_chunk(chunk_id: uuid.UUID, chunk_update: DataChunkUpdate, db: Session = Depends(get_db)):
    """Update a data chunk"""
    db_chunk = update_data_chunk(db, chunk_id=chunk_id, chunk_update=chunk_update)
    if db_chunk is None:
        raise HTTPException(status_code=404, detail="Data chunk not found")
    return db_chunk

@app.delete("/chunks/{chunk_id}")
async def delete_chunk(chunk_id: uuid.UUID, db: Session = Depends(get_db)):
    """Delete a data chunk"""
    db_chunk = delete_data_chunk(db, chunk_id=chunk_id)
    if db_chunk is None:
        raise HTTPException(status_code=404, detail="Data chunk not found")
    return {"message": "Data chunk deleted successfully"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)