import pytest
from main import app


# Фікстура (fixture) для створення тестового клієнта
@pytest.fixture
def client():
    # Вмикаємо режим тестування у Flask
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_swagger_documentation_is_accessible(client):
    """Тестуємо, чи працює сторінка зі Swagger UI"""
    response = client.get('/apidocs/')
    assert response.status_code == 200
    # Flasgger використовує swagger-ui як id та клас у своєму HTML
    assert b"swagger-ui" in response.data

def test_flask_book_lifecycle(client):
    """Повний цикл: створення, отримання, лістинг та видалення книги"""
    # 1. Створюємо книгу (POST)
    new_book_data = {
        "title": "Flask Web Development",
        "author": "Miguel Grinberg",
        "year": 2018
    }
    create_response = client.post('/books', json=new_book_data)

    assert create_response.status_code == 201
    created_book = create_response.get_json()
    assert "id" in created_book
    assert created_book["title"] == "Flask Web Development"

    book_id = created_book["id"]

    # 2. Отримуємо конкретну книгу по ID (GET)
    get_response = client.get(f'/books/{book_id}')
    assert get_response.status_code == 200
    assert get_response.get_json()["id"] == book_id

    # 3. Перевіряємо отримання списку з пагінацією (GET)
    list_response = client.get('/books?limit=5&offset=0')
    assert list_response.status_code == 200
    assert isinstance(list_response.get_json(), list)
    assert len(list_response.get_json()) >= 1

    # 4. Видаляємо книгу (DELETE)
    delete_response = client.delete(f'/books/{book_id}')
    assert delete_response.status_code == 204

    # 5. Перевіряємо, що книга дійсно видалена (GET -> 404)
    get_deleted_response = client.get(f'/books/{book_id}')
    assert get_deleted_response.status_code == 404