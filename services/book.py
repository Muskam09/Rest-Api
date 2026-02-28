from typing import List, Optional
from uuid import uuid4, UUID
from schemas.book import BookCreate, BookResponse, BookStatus
from repository.book import BookRepository

book_repo = BookRepository()


class BookService:
    async def get_books(
            self,
            status: Optional[BookStatus] = None,
            author: Optional[str] = None,
            sort_by: Optional[str] = None
    ) -> List[BookResponse]:
        # 1. Отримуємо всі сирі дані з "бази"
        books_data = await book_repo.get_all()

        # 2. Фільтрація
        if status:
            books_data = [b for b in books_data if b["status"] == status.value]
        if author:
            # Робимо пошук case-insensitive для зручності
            books_data = [b for b in books_data if b["author"].lower() == author.lower()]

        # 3. Сортування
        if sort_by == "title":
            books_data.sort(key=lambda x: x["title"].lower())
        elif sort_by == "year":
            books_data.sort(key=lambda x: x["year"])

        # 4. Мапимо словники назад у Pydantic схеми для відповіді
        return [BookResponse(**b) for b in books_data]

    async def get_book_by_id(self, book_id: UUID) -> Optional[BookResponse]:
        book_data = await book_repo.get_by_id(book_id)
        if book_data:
            return BookResponse(**book_data)
        return None

    async def create_book(self, book_in: BookCreate) -> BookResponse:
        # Перетворюємо Pydantic модель у словник
        book_dict = book_in.model_dump()
        # Генеруємо UUID
        book_dict["id"] = uuid4()

        created_book = await book_repo.create(book_dict)
        return BookResponse(**created_book)

    async def delete_book(self, book_id: UUID) -> bool:
        return await book_repo.delete(book_id)
