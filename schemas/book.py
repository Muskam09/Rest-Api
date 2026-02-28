from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from uuid import UUID


class BookStatus(str, Enum):
    available = "available in the library"
    issued = "issued to someone"


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the book")
    author: str = Field(..., min_length=1, description="Author of the book")
    description: Optional[str] = Field(None, description="Description")
    status: BookStatus = Field(default=BookStatus.available, description="Book status")
    year: int = Field(..., gt=0, description="Year of manufacture")

    # Змушуємо Pydantic віддавати статус як звичайний рядок (для БД)
    model_config = ConfigDict(use_enum_values=True)


class BookResponse(BookCreate):
    id: UUID

    # Головний фікс: дозволяємо Pydantic читати дані з об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)