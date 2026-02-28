from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from uuid import UUID

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book import BookService

router = APIRouter(prefix="/books", tags=["Books"])
book_service = BookService()

@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books(
    status_filter: Optional[BookStatus] = Query(None, alias="status", description="Filter by status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_by: Optional[str] = Query(None, description="Sort (title or year)")
):
    """Отримання списку книг з можливістю фільтрації та сортування."""
    return await book_service.get_books(status=status_filter, author=author, sort_by=sort_by)

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id: UUID):
    """Отримання книги за її ID."""
    book = await book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_in: BookCreate):
    """Додавання нової книги."""
    return await book_service.create_book(book_in)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID):
    """Видалення книги (ідемпотентний метод)."""
    deleted = await book_service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None