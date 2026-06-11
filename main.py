from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.book import router as book_router
from core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Створюємо таблиці в БД при старті (якщо їх немає)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Закриваємо з'єднання при вимкненні
    await engine.dispose()

app = FastAPI(
    title="Library REST API",
    description="API for library management with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(book_router)