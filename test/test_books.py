from fastapi.testclient import TestClient
from main import app


def test_cursor_pagination_and_lifecycle():
    with TestClient(app) as client:
        # 1. Створюємо ДВІ книги для перевірки пагінації
        book1_res = client.post(
            "/books/",
            json={"title": "Book A", "author": "Author A", "year": 2020, "status": "available in the library"}
        )
        book2_res = client.post(
            "/books/",
            json={"title": "Book B", "author": "Author B", "year": 2021, "status": "available in the library"}
        )

        assert book1_res.status_code == 201
        assert book2_res.status_code == 201

        # Оскільки ми сортуємо по UUID, ми не знаємо точно, яка буде першою.
        # Тому просто витягуємо першу сторінку з лімітом 1
        page1_res = client.get("/books/?limit=1")
        assert page1_res.status_code == 200
        page1_data = page1_res.json()
        assert len(page1_data) == 1

        # Беремо ID з першої сторінки, щоб використати як КУРСОР
        first_book_id = page1_data[0]["id"]

        # 2. Робимо запит за другою сторінкою, передаючи cursor
        page2_res = client.get(f"/books/?limit=1&cursor={first_book_id}")
        assert page2_res.status_code == 200
        page2_data = page2_res.json()
        assert len(page2_data) == 1

        # Перевіряємо, що це дійсно ІНША книга (id не співпадають)
        second_book_id = page2_data[0]["id"]
        assert first_book_id != second_book_id

        # 3. Видаляємо тестові дані
        client.delete(f"/books/{first_book_id}")
        client.delete(f"/books/{second_book_id}")