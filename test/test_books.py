import httpx
import pytest

# URL нашого мок-сервера (Prism)
MOCK_URL = "http://localhost:4010"


@pytest.mark.asyncio
async def test_mock_books_get_list():
    """Перевіряємо, що мок повертає список книг з правильною структурою"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MOCK_URL}/books/")

        # Перевіряємо статус
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Перевіряємо, що перший елемент має всі необхідни поля згідно зі схемою
        if len(data) > 0:
            book = data[0]
            assert "title" in book
            assert "author" in book
            assert "status" in book
            # Оскільки це мок, він повертає "string" замість реальних назв
            assert book["title"] == "string"


@pytest.mark.asyncio
async def test_mock_get_single_book():
    """Перевіряємо отримання однієї книги по ID"""
    async with httpx.AsyncClient() as client:
        # В Prism будь-який ID (наприклад '123') спрацює, якщо шлях підходить
        response = await client.get(f"{MOCK_URL}/books/any-id")

        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == "string"


@pytest.mark.asyncio
async def test_mock_create_book_validation():
    """Перевіряємо, як мок реагує на неправильні дані (валідація)"""
    async with httpx.AsyncClient() as client:
        # Відправляємо пустий об'єкт, хоча очікується BookCreate
        invalid_data = {}
        response = await client.post(f"{MOCK_URL}/books/", json=invalid_data)

        # Prism має автоматично повернути 422 або 400, бо дані не відповідають схемі
        assert response.status_code in [400, 422]