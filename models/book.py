import uuid
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="available in the library")
    year = Column(Integer, nullable=False)