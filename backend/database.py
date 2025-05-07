from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import enum
import json
import os

# Create async engine
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./presentations.db"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class StepStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "error"

class PresentationStep(enum.Enum):
    RESEARCH = "research"
    MANUAL_RESEARCH = "manual_research"
    SLIDES = "slides"
    IMAGES = "images"
    COMPILED = "compiled"
    PPTX = "pptx"

class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    topic = Column(String)
    author = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = relationship("PresentationStepModel", back_populates="presentation", cascade="all, delete-orphan")

class PresentationStepModel(Base):
    __tablename__ = "presentation_steps"

    id = Column(Integer, primary_key=True, index=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"))
    step = Column(String, nullable=False)
    status = Column(String, default=StepStatus.PENDING.value)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    presentation = relationship("Presentation", back_populates="steps")

    def set_result(self, data):
        self.result = json.dumps(data)
    
    def get_result(self):
        if not self.result:
            return None
        
        try:
            return json.loads(self.result)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for step {self.id}: {str(e)}")
            
            # Try to fix common JSON issues
            try:
                # Handle escaped characters
                cleaned = self.result.replace('\\\\', '\\')
                return json.loads(cleaned)
            except:
                pass
                
            try:
                # Try to extract content from partial JSON
                if self.result.startswith('{'):
                    # It might be a malformed JSON object
                    return {"content": "Error parsing JSON data", "error": "Data corruption detected"}
                else:
                    # It might be just plain text
                    return {"content": self.result[:1000] + "...(truncated)" if len(self.result) > 1000 else self.result}
            except:
                # Fallback to empty result
                return {"error": "Unable to parse result data"}

# Async context manager for database sessions
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

# Initialize the database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 