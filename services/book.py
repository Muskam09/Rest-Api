from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.book import BookCreate, BookResponse, BookStatus, PaginatedBookResponse
from repository.book import BookRepository


class BookService:
    # 1. Замість AsyncSession приймаємо об'єкт бази даних MongoDB
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = BookRepository(db)

    async def get_books(
            self,
            limit: int = 10,
            offset: int = 0,  # 2. Повертаємо offset замість cursor
            status: Optional[BookStatus] = None,
            author: Optional[str] = None
    ) -> PaginatedBookResponse:
        status_val = status.value if status else None

        books_data, total_count = await self.repo.get_all(
            limit=limit,
            offset=offset,
            status=status_val,
            author=author
        )
        validated_books = [BookResponse.model_validate(b) for b in books_data]

        return PaginatedBookResponse(
            data=validated_books,
            meta={
                "total_items": total_count,
                "limit": limit,
                "offset": offset
            }
        )

    # 3. book_id тепер має тип str (рядок), а не UUID
    async def get_book_by_id(self, book_id: str) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(book_id)
        if book:
            return BookResponse.model_validate(book)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        created_book = await self.repo.create(book_in.model_dump())
        return BookResponse.model_validate(created_book)

    # 3. book_id тепер має тип str
    async def delete_book(self, book_id: str) -> bool:
        return await self.repo.delete(book_id)