from fastapi import FastAPI
from api.book import router as book_router
from api.auth import router as auth_router  # Беремо роутер з нашого крутого файлу

app = FastAPI(
    title="Library REST API",
    description="API with MongoDB, JWT Auth and Redis Rate Limiting",
    version="5.0.0"
)

app.include_router(auth_router)
app.include_router(book_router)