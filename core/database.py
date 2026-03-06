import os
from pymongo import MongoClient

# Беремо URL з environment variables, або дефолтний для локального тесту
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_admin:password@localhost:27017")

# Ініціалізація синхронного Mongo клієнта
client = MongoClient(MONGO_URL)

# Вибираємо базу даних 'books' та колекцію 'books'
db = client.books
collection = db.books