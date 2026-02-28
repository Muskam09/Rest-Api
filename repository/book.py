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
        offset: int = 0,
        status: Optional[str] = None,
        author: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Book]:
        query = select(Book)

        if status:
            query = query.where(Book.status == status)
        if author:
            query = query.where(Book.author == author)

        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "year":
            query = query.order_by(Book.year)

        query = query.limit(limit).offset(offset)

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