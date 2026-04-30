from typing import List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

class BookRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.books

    async def get_all(
            self,
            limit: int = 10,
            offset: int = 0,
            status: Optional[str] = None,
            author: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        query = {}
        if status:
            query["status"] = status
        if author:
            query["author"] = author

        # 1. Рахуємо загальну кількість документів у Mongo
        total_count = await self.collection.count_documents(query)

        # 2. Витягуємо самі дані
        cursor = self.collection.find(query).skip(offset).limit(limit)
        books = await cursor.to_list(length=limit)
        
        return books, total_count

    async def get_by_id(self, book_id: str) -> Optional[dict]:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return None
        return await self.collection.find_one({"_id": obj_id})

    async def create(self, book_data: dict) -> dict:
        result = await self.collection.insert_one(book_data)
        book_data["_id"] = result.inserted_id
        return book_data

    async def delete(self, book_id: str) -> bool:
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return False
        result = await self.collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0