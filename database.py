import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

# Загрузка переменных окружения
load_dotenv()

# Глобальная переменная для соединения с базой данных
db: Optional[Database] = None

def get_database() -> Database:
    """
    Получение экземпляра базы данных.
    """
    if db is None:
        init_db()
    return db

def init_db() -> None:
    """
    Инициализация соединения с базой данных MongoDB.
    """
    global db
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.getenv("MONGO_DB", "isreal_db")
    
    try:
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        
        # Создание индексов для коллекций
        db.users.create_index("username", unique=True)
        db.users.create_index("telegram_id", unique=True)
        db.users.create_index("email", unique=True, sparse=True)
        
        db.sessions.create_index("owner_id")
        db.sessions.create_index("participants.user_id")
        
        db.auth_tokens.create_index("telegram_id", unique=True)
        db.auth_tokens.create_index("token", unique=True)
        db.auth_tokens.create_index("expires_at", expireAfterSeconds=0)
        
        print(f"База данных {mongo_db} успешно инициализирована")
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise

# Создание стартовых данных (если нужно)
def create_initial_data():
    """
    Создание начальных данных в базе, если они отсутствуют.
    """
    db = get_database()
    
    # Проверка и создание коллекции game_steps, если она пуста
    if db.game_steps.count_documents({}) == 0:
        steps = [
            {
                "step_id": 1,
                "title": "Определи проблему",
                "description": "Определи, что бесит — факты, а не мнения",
                "emoji": "1️⃣",
                "order": 1
            },
            {
                "step_id": 2,
                "title": "Выдели конфликт",
                "description": "Выдели два конфликтующих фактора",
                "emoji": "2️⃣",
                "order": 2
            },
            {
                "step_id": 3,
                "title": "Оформи локер",
                "description": "Оформи это как локер",
                "emoji": "3️⃣",
                "order": 3
            },
            {
                "step_id": 4,
                "title": "Копай глубже",
                "description": "Копай глубже — спрашивай «Почему?» 5 раз",
                "emoji": "4️⃣",
                "order": 4
            },
            {
                "step_id": 5,
                "title": "Переверни локер",
                "description": "Переверни локер",
                "emoji": "5️⃣",
                "order": 5
            },
            {
                "step_id": 6,
                "title": "Сформулируй ИКР",
                "description": "ИКР — это не магия, а хак реальности",
                "emoji": "🌀",
                "order": 6
            },
            {
                "step_id": 7,
                "title": "Поиск аналогий",
                "description": "Доведи до абсурда и ищи аналогии",
                "emoji": "🔍",
                "order": 7
            },
            {
                "step_id": 8,
                "title": "Финальные инсайты",
                "description": "Финальные инсайты и решения",
                "emoji": "💡",
                "order": 8
            }
        ]
        db.game_steps.insert_many(steps)
        print("Созданы начальные данные для шагов игры")

if __name__ == "__main__":
    # Для тестирования соединения с базой данных
    init_db()
    create_initial_data() 