from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.book import Book

class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        limit: int = 10,
        cursor: Optional[UUID] = None,
        status: Optional[str] = None,
        author: Optional[str] = None
    ) -> List[Book]:
        # Для курсорної пагінації базове сортування має бути незмінним (наприклад, по ID)
        query = select(Book).order_by(Book.id)

        # Фільтрація по статусу та автору
        if status:
            query = query.where(Book.status == status)
        if author:
            query = query.where(Book.author == author)

        # Логіка КУРСОРУ: беремо тільки ті записи, id яких "більший" за курсор
        if cursor:
            query = query.where(Book.id > cursor)

        # Ліміт залишається
        query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        query = select(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create(self, book_data: dict) -> Book:
        db_book = Book(**book_data)
        self.session.add(db_book)
        await self.session.commit()
        await self.session.refresh(db_book)
        return db_book

    async def delete(self, book_id: UUID) -> bool:
        query = delete(Book).where(Book.id == book_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0