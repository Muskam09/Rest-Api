from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.book import BookCreate, BookResponse, BookStatus, PaginatedBookResponse
from services.book import BookService
from core.database import get_db

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> BookService:
    return BookService(db)

# === ОНОВЛЕНО response_model ===
@router.get("/", response_model=PaginatedBookResponse, status_code=status.HTTP_200_OK, response_model_by_alias=False)
async def get_books(
    limit: int = Query(10, ge=1, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    status_filter: Optional[BookStatus] = Query(None, alias="status", description="Filter by status"),
    author: Optional[str] = Query(None, description="Filter by author"),
    service: BookService = Depends(get_book_service)
):
    """Get list of books with Limit-Offset pagination (MongoDB + Metadata)."""
    return await service.get_books(
        limit=limit,
        offset=offset,
        status=status_filter,
        author=author
    )

@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK, response_model_by_alias=False)
async def get_book(book_id: str, service: BookService = Depends(get_book_service)):
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_book(book_in: BookCreate, service: BookService = Depends(get_book_service)):
    return await service.create_book(book_in)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, service: BookService = Depends(get_book_service)):
    deleted = await service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None