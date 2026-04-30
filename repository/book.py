from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select, delete, func
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
    ) -> Tuple[List[Book], int]:
        query = select(Book)
        count_query = select(func.count()).select_from(Book)

        #фільтри ОДНОЧАСНО до обох запитів
        if status:
            query = query.where(Book.status == status)
            count_query = count_query.where(Book.status == status)
        if author:
            query = query.where(Book.author == author)
            count_query = count_query.where(Book.author == author)

        #запит на підрахунок загальної кількості (до накладання лімітів)
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar() or 0

        if sort_by == "title":
            query = query.order_by(Book.title)
        elif sort_by == "year":
            query = query.order_by(Book.year)

        # пагінацію
        query = query.limit(limit).offset(offset)

        #запит на отримання даних
        result = await self.session.execute(query)
        books = list(result.scalars().all())

        return books, total_count

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