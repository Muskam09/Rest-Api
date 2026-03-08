import time
import os
import redis.asyncio as redis
from fastapi import Request, HTTPException

# Підключення до Redis (беремо з env, або localhost для локальних тестів)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# Задаємо ліміти: (кількість_запитів, період_у_секундах)
RATE_LIMITS = {
    "anonymous": (2, 60),  # 2 запити на хвилину для анонімів
    "authenticated": (10, 60),  # 10 запитів на хвилину для авторизованих
}


async def rate_limit(request: Request, user_id: str | None = None):
    # Якщо user_id є, користувач авторизований. Інакше ідентифікуємо за IP
    identity = user_id or request.client.host
    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit:{limit_type}:{identity}"
    now = int(time.time())
    window_start = now - period

    # 1. Очищаємо старі записи, які випали за межі часового вікна
    await redis_client.zremrangebyscore(key, min=0, max=window_start)

    # 2. Рахуємо кількість запитів у поточному вікні
    request_count = await redis_client.zcard(key)

    # 3. Якщо ліміт перевищено, кидаємо помилку 429
    if request_count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")

    # 4. Якщо все ок, додаємо поточний запит у Redis
    # Використовуємо мапінг, де і значення, і score дорівнюють 'now'
    await redis_client.zadd(key, {str(now): now})

    # Оновлюємо час життя ключа
    await redis_client.expire(key, period)