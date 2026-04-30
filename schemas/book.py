from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from pydantic_mongo import ObjectIdField

class BookStatus(str, Enum):
    available = "available in the library"
    issued = "issued to someone"

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: BookStatus = Field(default=BookStatus.available)
    year: int = Field(..., gt=0)
    model_config = ConfigDict(use_enum_values=True)

class BookResponse(BookCreate):
    id: ObjectIdField = Field(alias="_id")
    model_config = ConfigDict(populate_by_name=True)

# === НОВІ СХЕМИ ДЛЯ МЕТАДАНИХ ===
class PaginationMeta(BaseModel):
    total_items: int
    limit: int
    offset: int

class PaginatedBookResponse(BaseModel):
    data: List[BookResponse]
    meta: PaginationMeta