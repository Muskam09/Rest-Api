import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app
from api.book import get_book_service  # Імпортуємо залежність


# 1. Створюємо фейковий сервіс для книг, щоб відключити MongoDB на час тестів
class MockBookService:
    async def get_books(self, *args, **kwargs):
        return []  # Просто повертаємо порожній список


# 2. Підміняємо реальну залежність на нашу фейкову
app.dependency_overrides[get_book_service] = lambda: MockBookService()

client = TestClient(app)


# Допоміжна функція для отримання токена
def get_auth_token():
    response = client.post("/auth/login", data={"username": "admin", "password": "secret"})
    return response.json()["access_token"]


# Базовий декоратор для мокання Redis
mock_redis = lambda func: patch("core.rate_limiter.redis_client.zremrangebyscore", new_callable=AsyncMock)(
    patch("core.rate_limiter.redis_client.zadd", new_callable=AsyncMock)(
        patch("core.rate_limiter.redis_client.expire", new_callable=AsyncMock)(func)))


@mock_redis
@patch("core.rate_limiter.redis_client.zcard", new_callable=AsyncMock)
def test_anonymous_under_limit(mock_zcard, mock_expire, mock_zadd, mock_zrem):
    """Тест 1: Анонімний юзер ще не досяг ліміту (2 запити). Очікуємо 200 OK."""
    mock_zcard.return_value = 1
    response = client.get("/books/")
    assert response.status_code == 200


@mock_redis
@patch("core.rate_limiter.redis_client.zcard", new_callable=AsyncMock)
def test_anonymous_over_limit(mock_zcard, mock_expire, mock_zadd, mock_zrem):
    """Тест 2: Анонімний юзер досяг ліміту (2 запити). Очікуємо 429 Too Many Requests."""
    mock_zcard.return_value = 2
    response = client.get("/books/")
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"


@mock_redis
@patch("core.rate_limiter.redis_client.zcard", new_callable=AsyncMock)
def test_authenticated_under_limit(mock_zcard, mock_expire, mock_zadd, mock_zrem):
    """Тест 3: Авторизований юзер ще не досяг ліміту (10 запитів). Очікуємо 200 OK."""
    token = get_auth_token()
    mock_zcard.return_value = 9

    response = client.get("/books/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@mock_redis
@patch("core.rate_limiter.redis_client.zcard", new_callable=AsyncMock)
def test_authenticated_over_limit(mock_zcard, mock_expire, mock_zadd, mock_zrem):
    """Тест 4: Авторизований юзер досяг ліміту (10 запитів). Очікуємо 429 Too Many Requests."""
    token = get_auth_token()
    mock_zcard.return_value = 10

    response = client.get("/books/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 429
    assert response.json()["detail"] == "Too many requests"