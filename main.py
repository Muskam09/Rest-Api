from fastapi import FastAPI
from api.book import router as book_router

app = FastAPI(
    title="Library REST API",
    description="API для управління бібліотекою",
    version="1.0.0"
)

# Підключаємо наші ендпоінти
app.include_router(book_router)
