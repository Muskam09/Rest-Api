from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
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

    # Зберігаємо enum як строку в БД
    model_config = ConfigDict(use_enum_values=True)


class BookResponse(BookCreate):
    # ObjectIdField автоматично валідує і конвертує ObjectId з MongoDB
    # alias="_id" каже Pydantic: "в базі це поле називається _id, але клієнту віддавай як id"
    id: ObjectIdField = Field(alias="_id")

    # Дозволяємо Pydantic шукати поля за псевдонімами
    model_config = ConfigDict(populate_by_name=True)