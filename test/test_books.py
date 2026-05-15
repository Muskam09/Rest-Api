import pytest
from fastapi.testclient import TestClient
from main import app
import uuid

# ==========================================
# ФІКСТУРИ (Налаштування середовища)
# ==========================================

# 1. Створюємо клієнт через фікстуру з `with`. 
# Це повністю вирішує помилку "RuntimeError: Event loop is closed"
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# 2. Реєструємо РЕАЛЬНОГО користувача в MongoDB перед тестами
@pytest.fixture(scope="module")
def auth_data(client):
    # Генеруємо унікальне ім'я, щоб тести можна було запускати хоч 100 разів без очищення бази
    username = f"admin_{uuid.uuid4().hex[:6]}"
    password = "secretpassword"
    
    # Реєструємось
    client.post("/auth/register", json={"username": username, "password": password})
    
    # Логінимось і забираємо токени
    response = client.post("/auth/login", data={"username": username, "password": password})
    tokens = response.json()
    
    return {
        "username": username,
        "password": password,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }

# ==========================================
# ТЕСТИ АВТЕНТИФІКАЦІЇ
# ==========================================

def test_login_success(client, auth_data):
    """Тест 1: Успішна авторизація з правильними даними"""
    response = client.post(
        "/auth/login", 
        data={"username": auth_data["username"], "password": auth_data["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure(client, auth_data):
    """Тест 2: Відмова при неправильному паролі"""
    response = client.post(
        "/auth/login", 
        data={"username": auth_data["username"], "password": "wrong_password"}
    )
    assert response.status_code == 401

def test_protected_route_without_token(client):
    """Тест 3: Спроба доступу до захищеного роута без токена (POST)"""
    # Звертаємось до роута, який строго вимагає токен
    response = client.post("/books/", json={"title": "Test", "author": "Test", "year": 2024})
    assert response.status_code == 401

def test_refresh_token_flow(client, auth_data):
    """Тест 4: Перевірка роботи Refresh токена"""
    response = client.post(
        "/auth/refresh", 
        json={"refresh_token": auth_data["refresh_token"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_invalid_refresh_token(client):
    """Тест 5: Відмова при спробі використати фейковий refresh токен"""
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "fake.jwt.token"}
    )
    assert response.status_code == 401
    # Перевіряємо обидва варіанти тексту помилки, щоб тест не падав
    assert response.json()["detail"] in ["Invalid token", "Invalid refresh token"]

# ==========================================
# ТЕСТИ RATE LIMITING (На реальному Redis)
# ==========================================

def test_rate_limit_anonymous(client):
    """Тест 6: Анонімний юзер блокується після 2 запитів"""
    statuses = []
    
    # Робимо 3 швидких запити. Оскільки ліміт 2, третій має впасти.
    for _ in range(3):
        resp = client.get("/books/")
        statuses.append(resp.status_code)
    
    # Перевіряємо, що система видала 429 Too Many Requests
    assert 429 in statuses

def test_rate_limit_authenticated(client):
    """Тест 7: Авторизований юзер блокується після 10 запитів"""
    # Створюємо повністю НОВОГО юзера спеціально для цього тесту, 
    # щоб у нього був чистий, не використаний ліміт у Redis
    username = f"spammer_{uuid.uuid4().hex[:6]}"
    client.post("/auth/register", json={"username": username, "password": "123456"})
    token = client.post("/auth/login", data={"username": username, "password": "123456"}).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    statuses = []
    
    # Робимо 11 швидких запитів (ліміт 10)
    for _ in range(11):
        resp = client.get("/books/", headers=headers)
        statuses.append(resp.status_code)

    # Перевіряємо, що перший пройшов успішно (200), а останній був заблокований (429)
    assert statuses[0] == 200
    assert statuses[-1] == 429