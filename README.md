# Маркетинг-ассистент бот для Telegram

## Описание проекта

Маркетинг-ассистент - это Telegram-бот, который помогает маркетологам и владельцам бизнеса в различных маркетинговых задачах, используя искусственный интеллект. Бот предоставляет широкий спектр функций:

- **Управление проектами**: создание и отслеживание маркетинговых проектов и задач
- **Анализ документов**: анализ маркетинговых документов, статей, текстов, изображений с помощью ИИ
- **Транскрибация аудио**: преобразование голосовых сообщений и аудиофайлов в текст с использованием ElevenLabs
- **Веб-исследования**: поиск и анализ информации в интернете
- **Генерация идей**: предложение креативных маркетинговых идей с помощью ИИ
- **Анализ рыночных трендов**: выявление и анализ актуальных трендов в указанной отрасли
- **Аналитика сайта**: получение отчетов по Яндекс.Метрике в удобном формате
- **Отслеживание статуса проектов**: мониторинг прогресса маркетинговых кампаний
- **История диалогов**: сохранение всех разговоров с ботом в базе данных для дальнейшего использования

## Технический стек

Проект использует следующие технологии:

- **Python 3.8+** - основной язык разработки
- **Aiogram 3** - фреймворк для создания Telegram-ботов
- **PostgreSQL** - база данных для хранения информации
- **SQLAlchemy** - ORM для работы с базой данных
- **Anthropic Claude API** - мощный ИИ для работы с текстом и анализа документов
- **Google Gemini API** - ИИ для анализа изображений и мультимодальных данных
- **ElevenLabs API** - для преобразования речи в текст с высокой точностью
- **SerpAPI** - для интеграции поиска в интернете
- **APScheduler** - для отправки автоматических отчетов по расписанию
- **Яндекс.Метрика API** - для получения аналитики сайта

## Требования

Для работы с ботом необходимо:

1. Python 3.8 или выше
2. PostgreSQL сервер
3. Telegram Bot Token (получить у @BotFather)
4. API ключи для следующих сервисов:
   - Anthropic Claude API 
   - Google Gemini API
   - SerpAPI (для веб-поиска)
   - ElevenLabs API
   - OAuth токен и идентификатор счетчика Яндекс.Метрики

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/marketing-assistant-bot.git
cd marketing-assistant-bot
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных PostgreSQL

Создайте базу данных PostgreSQL:

```bash
sudo -u postgres psql
CREATE DATABASE marketerbot;
CREATE USER botuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE marketerbot TO botuser;
\q
```

### 4. Настройка параметров окружения

Скопируйте файл `.env.example` в `.env` и заполните его своими данными:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`, указав ваши API ключи и настройки базы данных:

```
# Telegram Bot API токен
BOT_TOKEN=your_telegram_bot_token_here

# API ключи для ИИ сервисов
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Настройки для веб-поиска
SERP_API_KEY=your_serp_api_key_here

# API ключ для Eleven Labs (транскрибация аудио)
ELEVEN_LABS_API_KEY=your_elevenlabs_api_key_here

# Настройки для Яндекс Метрики
YANDEX_METRIKA_TOKEN=your_yandex_metrika_token_here
YANDEX_METRIKA_COUNTER_ID=your_counter_id_here

# Настройки базы данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=marketerbot
DB_USER=botuser
DB_PASSWORD=yourpassword

# Другие настройки
MAX_FILE_SIZE_MB=50
```

### 5. Инициализация базы данных

При первом запуске бота база данных будет инициализирована автоматически.

### 6. Запуск бота

```bash
python main.py
```

## Использование

### Команды бота

- `/start` - Запуск бота и приветственное сообщение
- `/help` - Показать список доступных команд
- `/project` - Создать новый проект
- `/projects` - Посмотреть список существующих проектов
- `/search` - Искать информацию в интернете
- `/ideas` - Генерировать идеи для маркетинга
- `/market` - Анализировать рыночные тренды
- `/metrika` - Получить отчеты из Яндекс.Метрики

### Работа с файлами

Бот может анализировать различные типы файлов:

1. **Документы** (PDF, DOCX, TXT): отправьте файл боту и задайте вопрос о его содержимом
2. **Изображения** (JPG, PNG): отправьте изображение для анализа его содержимого
3. **Аудио** (MP3, WAV, OGG): отправьте аудиофайл или голосовое сообщение для транскрибации

### Автоматические отчеты

Бот отправляет автоматические отчеты из Яндекс.Метрики:
- Ежедневные отчеты в 10:00
- Еженедельные отчеты по понедельникам в 10:30
- Ежемесячные отчеты 1-го числа каждого месяца в 11:00

## Структура проекта

```
marketerbot/
├── ai/
│   ├── claude_api.py       # Интеграция с Claude API
│   ├── gemini_api.py       # Интеграция с Gemini API
│   └── web_search.py       # Модуль для веб-поиска
├── bot/
│   ├── bot.py              # Основной файл бота
│   └── scheduler.py        # Планировщик для автоматических отчетов
├── database/
│   ├── db_operations.py    # Операции с базой данных
│   └── models.py           # Модели данных
├── utils/
│   ├── file_processor.py   # Обработка файлов
│   └── yandex_metrika.py   # Работа с API Яндекс.Метрики
├── .env.example            # Пример конфигурационного файла
├── config.py               # Конфигурация приложения
├── main.py                 # Точка входа приложения
└── requirements.txt        # Зависимости проекта
```

## Запуск на сервере

### Настройка сервера

1. Обновите пакеты и установите необходимое ПО:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib git
```

2. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/marketing-assistant-bot.git
cd marketing-assistant-bot
```

3. Создайте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. Настройте PostgreSQL:

```bash
sudo -u postgres psql
CREATE DATABASE marketerbot;
CREATE USER botuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE marketerbot TO botuser;
\q
```

5. Скопируйте файл `.env.example` в `.env` и заполните его своими данными:

```bash
cp .env.example .env
nano .env
```

### Запуск с помощью systemd

1. Создайте systemd сервис:

```bash
sudo nano /etc/systemd/system/marketerbot.service
```

2. Добавьте следующее содержимое (замените пути на актуальные):

```
[Unit]
Description=Marketing Assistant Telegram Bot
After=network.target postgresql.service

[Service]
User=yourusername
Group=yourusername
WorkingDirectory=/path/to/marketing-assistant-bot
Environment="PATH=/path/to/marketing-assistant-bot/venv/bin"
ExecStart=/path/to/marketing-assistant-bot/venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Активируйте и запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable marketerbot
sudo systemctl start marketerbot
```

4. Проверьте статус:

```bash
sudo systemctl status marketerbot
```

### Использование Docker (альтернативный вариант)

1. Установите Docker:

```bash
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
```

2. Создайте файл `Dockerfile`:

```
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

3. Создайте файл `docker-compose.yml`:

```yaml
version: '3'

services:
  bot:
    build: .
    restart: always
    env_file: .env
    depends_on:
      - db
    
  db:
    image: postgres:14
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=yourpassword
      - POSTGRES_USER=botuser
      - POSTGRES_DB=marketerbot

volumes:
  postgres_data:
```

4. Запустите с помощью Docker Compose:

```bash
docker-compose up -d
```

5. Проверьте логи:

```bash
docker-compose logs -f bot
```

## Лицензия

Этот проект распространяется под лицензией MIT. 