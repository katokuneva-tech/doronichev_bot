# Конфигурация бота Дороничева

# Параметры генерации ответов
MAX_TOKENS = 1300  # Максимальная длина ответа
TEMPERATURE = 0.8  # Креативность (0.0-1.0, выше = креативнее)
MODEL = "gpt-4"  # Модель OpenAI

# Параметры RAG поиска
N_RESULTS = 5  # Количество фрагментов из базы знаний
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

# Логирование:
ENABLE_LOGGING = True
LOGS_FILE = "conversations.jsonl"

# Аналитика
ENABLE_ANALYTICS = True
ANALYTICS_FILE = "bot_analytics.json"
ADMIN_USER_ID = None  # Твой Telegram ID (узнаем позже)
