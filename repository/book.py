from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # Отримуємо колекцію 'books' з нашої бази даних
        self.collection = db.books

    async def get_all(
            self,
            limit: int = 10,
            offset: int = 0,
            status: Optional[str] = None,
            author: Optional[str] = None
    ) -> List[dict]:
        # Формуємо словник-фільтр
        query = {}
        if status:
            query["status"] = status
        if author:
            query["author"] = author

        # find() - синхронний метод, він просто конструює запит (повертає AsyncIOMotorCursor)
        cursor = self.collection.find(query).skip(offset).limit(limit)

        # Асинхронно вивантажуємо дані з курсора в список
        books = await cursor.to_list(length=limit)
        return books

    async def get_by_id(self, book_id: str) -> Optional[dict]:
        try:
            # Конвертуємо строковий ID у формат ObjectId для Mongo
            obj_id = ObjectId(book_id)
        except Exception:
            return None

        return await self.collection.find_one({"_id": obj_id})

    async def create(self, book_data: dict) -> dict:
        # Записуємо в базу
        result = await self.collection.insert_one(book_data)
        # Додаємо згенерований MongoDB ID до нашого словника, щоб повернути його клієнту
        book_data["_id"] = result.inserted_id
        return book_data

    async def delete(self, book_id: str) -> bool:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return False

        result = await self.collection.delete_one({"_id": obj_id})
        # deleted_count показує, скільки документів було видалено
        return result.deleted_count > 0