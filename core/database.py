import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Беремо URL з environment variables (встановлено в docker-compose), або дефолтний для локального тесту
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/library")

# Створюємо асинхронний engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сесій
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# declarative_base() створює базовий клас, від якого успадковуються всі наші ORM-моделі
Base = declarative_base()

# Dependency Injection для FastAPI ендпоінтів [cite: 298]
async def get_db():
    async with async_session() as session:
        yield session