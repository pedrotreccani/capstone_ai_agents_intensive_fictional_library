from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import Book
from schemas.book import BookCreate, BookUpdate

class BookRepository:
    """Repository layer for book database operations"""
    
    @staticmethod
    def create(db: Session, book: BookCreate) -> Book:
        """Create a new book"""
        db_book = Book(**book.model_dump())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    @staticmethod
    def get_by_id(db: Session, book_id: int) -> Optional[Book]:
        """Get a book by ID"""
        return db.query(Book).filter(Book.id == book_id).first()
    
    @staticmethod
    def get_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        """Get a book by ISBN"""
        return db.query(Book).filter(Book.isbn == isbn).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get all books with pagination"""
        return db.query(Book).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, book: Book, book_update: BookUpdate) -> Book:
        """Update a book"""
        update_data = book_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(book, key, value)
        
        from datetime import datetime
        book.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(book)
        return book
    
    @staticmethod
    def delete(db: Session, book: Book) -> None:
        """Delete a book"""
        db.delete(book)
        db.commit()
    
    @staticmethod
    def add_vote(db: Session, book: Book, stars: int) -> Book:
        """Add a vote to a book and update average rating"""
        total_rating = book.rating * book.vote_count
        book.vote_count += 1
        book.rating = (total_rating + stars) / book.vote_count
        
        from datetime import datetime
        book.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(book)
        return book