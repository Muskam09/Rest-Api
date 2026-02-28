from typing import List, Dict, Optional
from uuid import UUID
from models.book import books_db

class BookRepository:
    async def get_all(self) -> List[Dict]:
        return books_db

    async def get_by_id(self, book_id: UUID) -> Optional[Dict]:
        for book in books_db:
            if book["id"] == book_id:
                return book
        return None

    async def create(self, book_data: Dict) -> Dict:
        books_db.append(book_data)
        return book_data

    async def delete(self, book_id: UUID) -> bool:
        # Шукаємо книгу за ID та видаляємо
        for i, book in enumerate(books_db):
            if book["id"] == book_id:
                del books_db[i]
                return True # Успішно видалено
        return False # Книгу не знайдено