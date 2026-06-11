from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
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

    model_config = ConfigDict(use_enum_values=True)

class BookResponse(BookCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

class CursorPaginationMeta(BaseModel):
    total_items: int
    limit: int
    next_cursor: Optional[UUID] = None  # ID останнього елемента на цій сторінці

class CursorPaginatedBookResponse(BaseModel):
    data: List[BookResponse]
    meta: CursorPaginationMeta