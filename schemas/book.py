from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from uuid import UUID

# Визначаємо статуси через Enum для суворої типізації
class BookStatus(str, Enum):
    available = "available in the library"
    issued = "issued to someone"

# Базова схема для створення книги
class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    description: Optional[str] = Field(None, description="Description")
    status: BookStatus = Field(default=BookStatus.available, description="Book status")
    year: int = Field(..., gt=0, description="Year of manufacture")

# Схема для відповіді (додається ID)
class BookResponse(BookCreate):
    id: UUID
