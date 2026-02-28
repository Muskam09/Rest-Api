import pytest
from fastapi.testclient import TestClient
from main import app
from models.book import books_db

client = TestClient(app)

# Фікстура для очищення in-memory "бази" перед кожним тестом
@pytest.fixture(autouse=True)
def clear_database():
    books_db.clear()
    yield

def test_create_book():
    response = client.post(
        "/books/",
        json={
            "title": "Kobzar",
            "author": "Taras Shevchenko",
            "year": 1840,
            "status": "available in the library"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Kobzar"
    assert "id" in data

def test_get_books_with_filter():
    # Додаємо тестові дані
    client.post("/books/", json={"title": "Book 1", "author": "Autor 1", "year": 2000, "status": "available in the library"})
    client.post("/books/", json={"title": "Book 2", "author": "Autor Б", "year": 2010, "status": "issued to someone"})

    # Тестуємо фільтр
    response = client.get("/books/?status=available in the library")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Book 1"

def test_get_book_by_id():
    create_response = client.post("/books/", json={"title": "1984", "author": "George Orwell", "year": 1949})
    book_id = create_response.json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["id"] == book_id

def test_delete_book_idempotent():
    create_response = client.post("/books/", json={"title": "Shadows of Forgotten Ancestors", "author": "Mykhailo Kotsyubynskyi", "year": 1911})
    book_id = create_response.json()["id"]

    # Перший запит: видалення (очікуємо 204)
    delete_response_1 = client.delete(f"/books/{book_id}")
    assert delete_response_1.status_code == 204

    # Другий запит: об'єкт вже видалено, система не змінюється (очікуємо 404)
    delete_response_2 = client.delete(f"/books/{book_id}")
    assert delete_response_2.status_code == 404
