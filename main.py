from fastapi import FastAPI
from api.book import router as book_router

app = FastAPI(
    title="Library REST API",
    description="API for library management with MongoDB",
    version="3.0.0"
)

# Підключаємо наші ендпоінти
app.include_router(book_router)