from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Book(Base):
    """SQLAlchemy model for books table"""
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True)
    description = Column(String)
    published_year = Column(Integer)
    rating = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)