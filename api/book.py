from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import jwt

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book import BookService
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/books", tags=["Books"])

# Вказуємо FastAPI, куди Swagger має відправляти логін і пароль для отримання токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# перевіряє валідність JWT токена
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Декодуємо токен за допомогою нашого секретного ключа
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        # Перевіряємо, чи це дійсно access токен (а не refresh) і чи є там користувач
        if username is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return username

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_book_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> BookService:
    return BookService(db)


@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK, response_model_by_alias=False)
async def get_books(
        limit: int = Query(10, ge=1, description="Number of records to return"),
        offset: int = Query(0, ge=0, description="Number of records to skip"),
        status_filter: Optional[BookStatus] = Query(None, alias="status", description="Filter by status"),
        author: Optional[str] = Query(None, description="Filter by author"),
        service: BookService = Depends(get_book_service),
        current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    """Get list of books (Protected)."""
    return await service.get_books(limit=limit, offset=offset, status=status_filter, author=author)


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK, response_model_by_alias=False)
async def get_book(
        book_id: str,
        service: BookService = Depends(get_book_service),
        current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    """Get a book by its ID (Protected)."""
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED, response_model_by_alias=False)
async def create_book(
        book_in: BookCreate,
        service: BookService = Depends(get_book_service),
        current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    """Add a new book (Protected)."""
    return await service.create_book(book_in)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        book_id: str,
        service: BookService = Depends(get_book_service),
        current_user: str = Depends(get_current_user)  # <--- ЗАХИСТ
):
    """Delete a book (Protected)."""
    deleted = await service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None