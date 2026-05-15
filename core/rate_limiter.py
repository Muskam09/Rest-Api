import os
import time
import uuid  # <--- Додаємо імпорт uuid
import redis.asyncio as redis
from fastapi import Request, HTTPException

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

RATE_LIMITS = {
    "anonymous": (2, 60),  
    "authenticated": (10, 60), 
}

async def rate_limit(request: Request, user_id: str | None = None):
    # У тестах request.client може бути None, тому додаємо fallback "127.0.0.1"
    ip = request.client.host if request.client else "127.0.0.1"
    identity = user_id or ip

    limit_type = "authenticated" if user_id else "anonymous"
    limit, period = RATE_LIMITS[limit_type]

    key = f"rate_limit:{limit_type}:{identity}"
    
    # Залишаємо float, щоб враховувати мілісекунди
    now = time.time() 
    window_start = now - period

    # 1. Очищаємо старі записи
    await redis_client.zremrangebyscore(key, min=0, max=window_start)

    # 2. Рахуємо кількість запитів
    request_count = await redis_client.zcard(key)

    # 3. Перевіряємо ліміт
    if request_count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")

    # 4. Робимо запис УНІКАЛЬНИМ за допомогою uuid
    unique_member = f"{now}-{uuid.uuid4().hex}"
    await redis_client.zadd(key, {unique_member: now})

    # Оновлюємо час життя
    await redis_client.expire(key, period)