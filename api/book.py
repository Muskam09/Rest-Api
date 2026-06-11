from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.book import BookCreate, BookResponse, BookStatus, CursorPaginatedBookResponse
from services.book import BookService
from core.database import get_db

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(session: AsyncSession = Depends(get_db)) -> BookService:
    return BookService(session)

@router.get("/", response_model=CursorPaginatedBookResponse, status_code=status.HTTP_200_OK)
async def get_books(
    limit: int = Query(10, ge=1, description="Number of records to return"),
    cursor: Optional[UUID] = Query(None, description="Cursor (ID of the last item from the previous page)"),
    status_filter: Optional[BookStatus] = Query(None, alias="status", description="Filter by status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    service: BookService = Depends(get_book_service)
):
    """Get list of books using Cursor pagination (with metadata)."""
    return await service.get_books(
        limit=limit,
        cursor=cursor,
        status=status_filter,
        author=author
    )

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(book_id: UUID, service: BookService = Depends(get_book_service)):
    """Get a book by its ID."""
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_in: BookCreate, service: BookService = Depends(get_book_service)):
    """Add a new book."""
    return await service.create_book(book_in)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: UUID, service: BookService = Depends(get_book_service)):
    """Delete a book (idempotent)."""
    deleted = await service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None