from fastapi import APIRouter, HTTPException, Query, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import jwt

from schemas.book import BookCreate, BookResponse, BookStatus
from services.book import BookService
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from core.rate_limiter import rate_limit  # Імпортуємо наш Rate Limiter

router = APIRouter(prefix="/books", tags=["Books"])

# auto_error=False дозволяє нам робити токен необов'язковим для деяких ендпоінтів
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

# Строга залежність для захищених роутів (кидає 401, якщо токена немає)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return username
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

# Необов'язкова залежність для публічних роутів (повертає None, якщо токена немає)
async def get_optional_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None

def get_book_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> BookService:
    return BookService(db)

# ==========================================
# ЕНДПОІНТИ
# ==========================================

@router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK)
async def get_books(
    request: Request,  # Додаємо Request для лімітера
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    service: BookService = Depends(get_book_service),
    current_user: Optional[str] = Depends(get_optional_user) # Може бути None
):
    # Викликаємо лімітер. Якщо current_user == None, ліміт буде 2 запити/хв. Якщо авторизований — 10.
#   await rate_limit(request, current_user)
    return await service.get_books(limit=limit, offset=offset)


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    request: Request,  # Додаємо Request
    book_in: BookCreate,
    service: BookService = Depends(get_book_service),
    current_user: str = Depends(get_current_user)  # Строга авторизація
):
    # Тут current_user гарантовано є, ліміт буде 10 запитів/хв
#   await rate_limit(request, current_user)
    return await service.create_book(book_in)


@router.get("/{book_id}", response_model=BookResponse, status_code=status.HTTP_200_OK)
async def get_book(
    request: Request,
    book_id: str,
    service: BookService = Depends(get_book_service),
    current_user: Optional[str] = Depends(get_optional_user)
):
#   await rate_limit(request, current_user)
    book = await service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    request: Request,
    book_id: str,
    service: BookService = Depends(get_book_service),
    current_user: str = Depends(get_current_user)
):
#   await rate_limit(request, current_user)
    deleted = await service.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return None
