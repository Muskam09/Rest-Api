from fastapi.testclient import TestClient
from main import app

def test_mongodb_book_lifecycle():
    with TestClient(app) as client:
        # 1. Тестуємо створення книги (POST)
        create_response = client.post(
            "/books/",
            json={
                "title": "MongoDB: The Definitive Guide",
                "author": "Shannon Bradshaw",
                "year": 2019,
                "status": "available in the library"
            }
        )
        assert create_response.status_code == 201
        created_book = create_response.json()

        assert "id" in created_book
        assert created_book["title"] == "MongoDB: The Definitive Guide"

        book_id = created_book["id"]
        assert isinstance(book_id, str)
        assert len(book_id) == 24

        # 2. Тестуємо отримання книги по ID (GET)
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == book_id

        # 3. Тестуємо отримання списку з метаданими (GET)
        list_response = client.get("/books/?limit=5&offset=0")
        assert list_response.status_code == 200
        
        response_json = list_response.json()
        
        # Перевірка нової структури з метаданими
        assert "data" in response_json
        assert "meta" in response_json
        assert isinstance(response_json["data"], list)
        assert len(response_json["data"]) >= 1
        
        assert response_json["meta"]["limit"] == 5
        assert response_json["meta"]["offset"] == 0
        assert response_json["meta"]["total_items"] >= 1

        # 4. Тестуємо ідемпотентне видалення (DELETE)
        delete_response_1 = client.delete(f"/books/{book_id}")
        assert delete_response_1.status_code == 204

        delete_response_2 = client.delete(f"/books/{book_id}")
        assert delete_response_2.status_code == 404