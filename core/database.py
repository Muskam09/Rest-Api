import os
import motor.motor_asyncio

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")

# Асинхронний MongoDB клієнт ініціалізується
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Вибираємо базу даних 'books'
db = client.books

# Dependency Injection для FastAPI
async def get_db():
    yield db