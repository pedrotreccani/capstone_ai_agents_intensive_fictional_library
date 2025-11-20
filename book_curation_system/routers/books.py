from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.book import BookCreate, BookUpdate, BookResponse, VoteRequest
from services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Books"])
book_service = BookService()

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    return book_service.create_book(db, book)

@router.get("", response_model=List[BookResponse])
async def list_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all books with pagination"""
    return book_service.list_books(db, skip, limit)

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID"""
    return book_service.get_book(db, book_id)

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db)
):
    """Update a book"""
    return book_service.update_book(db, book_id, book_update)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book"""
    book_service.delete_book(db, book_id)
    return None

@router.post("/{book_id}/vote", response_model=BookResponse)
async def vote_book(
    book_id: int,
    vote: VoteRequest,
    db: Session = Depends(get_db)
):
    """Vote on a book with 0-5 stars"""
    return book_service.vote_on_book(db, book_id, vote)