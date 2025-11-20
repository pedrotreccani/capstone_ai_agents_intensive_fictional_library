from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    """Base book schema with common fields"""
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    published_year: Optional[int] = None

class BookCreate(BookBase):
    """Schema for creating a new book"""
    pass

class BookUpdate(BaseModel):
    """Schema for updating a book - all fields optional"""
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None

class BookResponse(BookBase):
    """Schema for book responses including computed fields"""
    id: int
    rating: float
    vote_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VoteRequest(BaseModel):
    """Schema for voting on a book"""
    stars: int = Field(..., ge=0, le=5, description="Rating from 0 to 5 stars")

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    region: Optional[str]
    zone: Optional[str]
    timestamp: datetime