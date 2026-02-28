from fastapi.testclient import TestClient
from main import app


def test_full_book_lifecycle():
    # Використовуємо 'with', щоб база не закривалася між запитами
    with TestClient(app) as client:
        # 1. Тестуємо створення книги (POST)
        create_response = client.post(
            "/books/",
            json={
                "title": "Kubernetes Up & Running",
                "author": "Kelsey Hightower",
                "year": 2017,
                "status": "available in the library"
            }
        )
        assert create_response.status_code == 201
        created_book = create_response.json()
        assert "id" in created_book
        assert created_book["title"] == "Kubernetes Up & Running"

        book_id = created_book["id"]

        # 2. Тестуємо отримання книги по ID (GET)
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == book_id

        # 3. Тестуємо отримання списку з пагінацією Limit-Offset (GET)
        list_response = client.get("/books/?limit=5&offset=0")
        assert list_response.status_code == 200
        assert isinstance(list_response.json(), list)
        assert len(list_response.json()) >= 1

        # 4. Тестуємо ідемпотентне видалення (DELETE)
        # Перший запит - успішно видаляє (204)
        delete_response_1 = client.delete(f"/books/{book_id}")
        assert delete_response_1.status_code == 204

        # Другий запит - ресурсу вже немає (404)
        delete_response_2 = client.delete(f"/books/{book_id}")
        assert delete_response_2.status_code == 404