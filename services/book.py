from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book import BookRepository


class BookService:
    def __init__(self, session: AsyncSession):
        self.repo = BookRepository(session)

    async def get_books(
            self,
            limit: int = 10,
            offset: int = 0,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            sort_by: Optional[str] = None
    ) -> List[BookResponse]:
        # Витягуємо строкове значення з Enum для передачі в БД
        status_val = status.value if status else None

        books = await self.repo.get_all(
            limit=limit,
            offset=offset,
            status=status_val,
            author=author,
            sort_by=sort_by
        )
        # model_validate автоматично перетворює ORM об'єкт у Pydantic схему
        return [BookResponse.model_validate(b) for b in books]

    async def get_book_by_id(self, book_id: UUID) -> Optional[BookResponse]:
        book = await self.repo.get_by_id(book_id)
        if book:
            return BookResponse.model_validate(book)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        # model_dump перетворює Pydantic схему у словник для SQLAlchemy
        created_book = await self.repo.create(book_in.model_dump())
        return BookResponse.model_validate(created_book)

    async def delete_book(self, book_id: UUID) -> bool:
        return await self.repo.delete(book_id)