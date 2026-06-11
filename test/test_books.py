from fastapi.testclient import TestClient
from main import app

def test_cursor_pagination_and_lifecycle():
    with TestClient(app) as client:
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

        page1_res = client.get("/books/?limit=1")
        assert page1_res.status_code == 200
        page1_json = page1_res.json()

        assert "data" in page1_json
        assert "meta" in page1_json
        assert len(page1_json["data"]) == 1
        next_cursor = page1_json["meta"]["next_cursor"]
        first_book_id = page1_json["data"][0]["id"]

        assert next_cursor == first_book_id

        page2_res = client.get(f"/books/?limit=1&cursor={next_cursor}")
        assert page2_res.status_code == 200
        page2_json = page2_res.json()
        assert len(page2_json["data"]) == 1

        second_book_id = page2_json["data"][0]["id"]
        assert first_book_id != second_book_id

        client.delete(f"/books/{first_book_id}")
        client.delete(f"/books/{second_book_id}")