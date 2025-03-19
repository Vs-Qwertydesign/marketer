import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Telegram Bot API токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API ключи для ИИ сервисов
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Настройки для веб-поиска
SERP_API_KEY = os.getenv("SERP_API_KEY")

# API ключ для Eleven Labs (транскрибация аудио)
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

# Настройки для Яндекс Метрики
YANDEX_METRIKA_TOKEN = os.getenv("YANDEX_METRIKA_TOKEN")
YANDEX_METRIKA_COUNTER_ID = os.getenv("YANDEX_METRIKA_COUNTER_ID")

# Настройки базы данных
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "marketerbot")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Настройки для ИИ
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Другие настройки
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
MAX_TOKENS_RESPONSE = int(os.getenv("MAX_TOKENS_RESPONSE", 4000))
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ru") 