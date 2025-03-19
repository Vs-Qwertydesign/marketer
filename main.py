import asyncio
import logging
import os
import sys
from aiogram import Bot

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BOT_TOKEN
from database.db_operations import init_db
from bot.bot import main as bot_main
from bot.scheduler import start_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def startup():
    """
    Выполняет необходимые действия при запуске приложения
    """
    try:
        # Инициализируем базу данных
        logger.info("Инициализация базы данных...")
        init_db()
        logger.info("База данных инициализирована успешно")
        
        # Запускаем планировщик в отдельной задаче
        scheduler_task = asyncio.create_task(start_scheduler())
        logger.info("Планировщик задач запущен")
        
        # Запускаем бота
        logger.info("Запуск бота...")
        await bot_main()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise

if __name__ == "__main__":
    # Запускаем приложение
    try:
        asyncio.run(startup())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 