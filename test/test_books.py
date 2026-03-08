from fastapi.testclient import TestClient
from main import app

# Створюємо тестовий клієнт
client = TestClient(app)

def test_login_success():
    """Тест 1: Успішна авторизація з правильними даними"""
    response = client.post(
        "/auth/login", 
        data={"username": "admin", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    """Тест 2: Відмова при неправильному паролі"""
    response = client.post(
        "/auth/login", 
        data={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route_without_token():
    """Тест 3: Спроба доступу до захищеного роута без токена"""
    response = client.get("/books/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_protected_route_with_token():
    """Тест 4: Успішний доступ до захищеного роута з валідним токеном"""
    # 1. Спочатку логінимось, щоб отримати токен
    login_response = client.post(
        "/auth/login", 
        data={"username": "admin", "password": "secret"}
    )
    access_token = login_response.json()["access_token"]

    # 2. Робимо запит до книг, передаючи токен у заголовку Authorization
    response = client.get(
        "/books/", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_refresh_token_flow():
    """Тест 5: Перевірка роботи Refresh токена"""
    # 1. Отримуємо refresh_token
    login_response = client.post(
        "/auth/login", 
        data={"username": "admin", "password": "secret"}
    )
    refresh_token = login_response.json()["refresh_token"]

    # 2. Відправляємо refresh_token для отримання нового access_token
    refresh_response = client.post(
        "/auth/refresh", 
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_refresh_token():
    """Тест 6: Відмова при спробі використати фейковий refresh токен"""
    refresh_response = client.post(
        "/auth/refresh", 
        json={"refresh_token": "fake.jwt.token"}
    )
    assert refresh_response.status_code == 401
    assert refresh_response.json()["detail"] == "Invalid token"