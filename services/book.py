from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.book import BookCreate, BookResponse, BookStatus, CursorPaginatedBookResponse, CursorPaginationMeta
from repository.book import BookRepository

class BookService:
    def __init__(self, session: AsyncSession):
        self.repo = BookRepository(session)

    async def get_books(
            self,
            limit: int = 10,
            cursor: Optional[UUID] = None,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None
    ) -> CursorPaginatedBookResponse:
        status_val = status.value if status else None

        # Отримуємо книги та загальну кількість
        books, total_count = await self.repo.get_all(
            limit=limit,
            cursor=cursor,
            status=status_val,
            author=author
        )
        
        validated_books = [BookResponse.model_validate(b) for b in books]

        # Визначаємо next_cursor. Це ID останньої книги в поточному списку.
        # Якщо список порожній, next_cursor буде None.
        next_cursor = validated_books[-1].id if validated_books else None

        return CursorPaginatedBookResponse(
            data=validated_books,
            meta=CursorPaginationMeta(
                total_items=total_count,
                limit=limit,
                next_cursor=next_cursor
            )
        )

    async def get_book_by_id(self, book_id: UUID) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(book_id)
        if book:
            return BookResponse.model_validate(book)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        created_book = await self.repo.create(book_in.model_dump())
        return BookResponse.model_validate(created_book)

    async def delete_book(self, book_id: UUID) -> bool:
        return await self.repo.delete(book_id)