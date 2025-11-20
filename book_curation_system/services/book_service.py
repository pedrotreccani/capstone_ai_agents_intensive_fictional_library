from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from repositories.book_repository import BookRepository
from schemas.book import BookCreate, BookUpdate, BookResponse, VoteRequest
from config.telemetry import logger, tracer

class BookService:
    """Service layer for book business logic"""
    
    def __init__(self):
        self.repository = BookRepository()
    
    def create_book(self, db: Session, book: BookCreate) -> BookResponse:
        """Create a new book with validation"""
        with tracer.start_as_current_span("service_create_book"):
            # Check if ISBN already exists
            existing = self.repository.get_by_isbn(db, book.isbn)
            if existing:
                logger.warning(f"Attempted to create duplicate ISBN: {book.isbn}")
                raise HTTPException(status_code=400, detail="ISBN already exists")
            
            db_book = self.repository.create(db, book)
            logger.info(f"Created book: {db_book.title} (ID: {db_book.id})")
            return BookResponse.model_validate(db_book)
    
    def get_book(self, db: Session, book_id: int) -> BookResponse:
        """Get a book by ID"""
        with tracer.start_as_current_span("service_get_book"):
            book = self.repository.get_by_id(db, book_id)
            if not book:
                logger.warning(f"Book not found: {book_id}")
                raise HTTPException(status_code=404, detail="Book not found")
            
            logger.info(f"Retrieved book: {book.title} (ID: {book_id})")
            return BookResponse.model_validate(book)
    
    def list_books(self, db: Session, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """List all books with pagination"""
        with tracer.start_as_current_span("service_list_books"):
            books = self.repository.get_all(db, skip, limit)
            logger.info(f"Retrieved {len(books)} books")
            return [BookResponse.model_validate(book) for book in books]
    
    def update_book(self, db: Session, book_id: int, book_update: BookUpdate) -> BookResponse:
        """Update a book with validation"""
        with tracer.start_as_current_span("service_update_book"):
            book = self.repository.get_by_id(db, book_id)
            if not book:
                logger.warning(f"Book not found for update: {book_id}")
                raise HTTPException(status_code=404, detail="Book not found")
            
            # Check ISBN uniqueness if being updated
            if book_update.isbn and book_update.isbn != book.isbn:
                existing = self.repository.get_by_isbn(db, book_update.isbn)
                if existing:
                    raise HTTPException(status_code=400, detail="ISBN already exists")
            
            updated_book = self.repository.update(db, book, book_update)
            logger.info(f"Updated book: {updated_book.title} (ID: {book_id})")
            return BookResponse.model_validate(updated_book)
    
    def delete_book(self, db: Session, book_id: int) -> None:
        """Delete a book"""
        with tracer.start_as_current_span("service_delete_book"):
            book = self.repository.get_by_id(db, book_id)
            if not book:
                logger.warning(f"Book not found for deletion: {book_id}")
                raise HTTPException(status_code=404, detail="Book not found")
            
            self.repository.delete(db, book)
            logger.info(f"Deleted book ID: {book_id}")
    
    def vote_on_book(self, db: Session, book_id: int, vote: VoteRequest) -> BookResponse:
        """Add a vote to a book"""
        with tracer.start_as_current_span("service_vote_book"):
            book = self.repository.get_by_id(db, book_id)
            if not book:
                logger.warning(f"Book not found for voting: {book_id}")
                raise HTTPException(status_code=404, detail="Book not found")
            
            updated_book = self.repository.add_vote(db, book, vote.stars)
            logger.info(
                f"Vote added to book {updated_book.title}: "
                f"{vote.stars} stars (new avg: {updated_book.rating:.2f})"
            )
            return BookResponse.model_validate(updated_book)