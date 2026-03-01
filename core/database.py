import os
import motor.motor_asyncio

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")

# Ініціалізація Mongo клієнта
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
# Вибираємо базу даних (якщо її немає - Mongo створить її автоматично при першому записі)
db = client.books

# Dependency Injection
async def get_db():
    yield db