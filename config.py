# Конфигурация бота Дороничева

import os

# Параметры генерации ответов
MAX_TOKENS = 2000  # Максимальная длина ответа
TEMPERATURE = 0.7  # Креативность (0.0-1.0, выше = креативнее)
MODEL = "gpt-4.1"  # Модель OpenAI

# Параметры RAG поиска
N_RESULTS = 3  # Количество фрагментов из базы знаний
EMBEDDING_MODEL = "text-embedding-3-large"  # Модель для эмбеддингов

# Параметры памяти
MAX_HISTORY_MESSAGES = 10  # Максимум сообщений в истории (пар вопрос-ответ)
HISTORY_CONTEXT_MESSAGES = 6  # Сколько последних сообщений отправлять в контекст

# Фильтр запрещенных тем
FORBIDDEN_TOPICS = ["политика", "религия", "медицина"]

# Пути к файлам
VECTOR_DB_PATH = "./doronichev_vectordb"
COLLECTION_NAME = "doronichev_knowledge"
SYSTEM_PROMPT_FILE = "system_prompt.txt"

# Аналитика
ENABLE_ANALYTICS = True
ANALYTICS_FILE = "bot_analytics.json"

# ADMIN_USER_ID: установить через env-переменную ADMIN_USER_ID (Telegram ID числом)
_admin_id = os.getenv("ADMIN_USER_ID")
ADMIN_USER_ID = int(_admin_id) if _admin_id else None

# Rate limiting: максимум сообщений от одного пользователя в минуту
RATE_LIMIT_MESSAGES = 5
RATE_LIMIT_WINDOW = 60  # секунд
