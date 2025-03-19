import asyncio
import logging
import sys
import os
from datetime import datetime, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKEN
from utils.yandex_metrika import get_daily_report, get_weekly_report, get_monthly_report
from database.db_operations import get_all_users

# Инициализируем бота
bot = Bot(token=BOT_TOKEN)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определяем функции для выполнения запланированных задач
async def send_daily_report():
    """Отправка ежедневного отчета по Яндекс.Метрике всем пользователям"""
    try:
        logging.info("Отправка ежедневного отчета по Яндекс.Метрике")
        
        # Получаем отчет
        report = get_daily_report()
        
        # Получаем всех пользователей
        users = get_all_users()
        
        # Отправляем отчет каждому пользователю
        for user in users:
            try:
                await bot.send_message(chat_id=user.telegram_id, text=report)
                logging.info(f"Отчет отправлен пользователю {user.telegram_id}")
                # Небольшая задержка между отправками сообщений
                await asyncio.sleep(0.5)
            except Exception as e:
                logging.error(f"Ошибка при отправке отчета пользователю {user.telegram_id}: {e}")
        
        logging.info("Ежедневный отчет успешно отправлен всем пользователям")
    except Exception as e:
        logging.error(f"Ошибка при отправке ежедневного отчета: {e}")

async def send_weekly_report():
    """Отправка еженедельного отчета по Яндекс.Метрике всем пользователям"""
    try:
        logging.info("Отправка еженедельного отчета по Яндекс.Метрике")
        
        # Получаем отчет
        report = get_weekly_report()
        
        # Получаем всех пользователей
        users = get_all_users()
        
        # Отправляем отчет каждому пользователю
        for user in users:
            try:
                await bot.send_message(chat_id=user.telegram_id, text=report)
                logging.info(f"Еженедельный отчет отправлен пользователю {user.telegram_id}")
                # Небольшая задержка между отправками сообщений
                await asyncio.sleep(0.5)
            except Exception as e:
                logging.error(f"Ошибка при отправке еженедельного отчета пользователю {user.telegram_id}: {e}")
        
        logging.info("Еженедельный отчет успешно отправлен всем пользователям")
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного отчета: {e}")

async def send_monthly_report():
    """Отправка ежемесячного отчета по Яндекс.Метрике всем пользователям"""
    try:
        logging.info("Отправка ежемесячного отчета по Яндекс.Метрике")
        
        # Получаем текущую дату
        now = datetime.now()
        
        # Проверяем, что сегодня первый день месяца
        if now.day != 1:
            logging.info("Сегодня не первый день месяца, пропускаем отправку ежемесячного отчета")
            return
        
        # Получаем отчет
        report = get_monthly_report()
        
        # Получаем всех пользователей
        users = get_all_users()
        
        # Отправляем отчет каждому пользователю
        for user in users:
            try:
                await bot.send_message(chat_id=user.telegram_id, text=report)
                logging.info(f"Ежемесячный отчет отправлен пользователю {user.telegram_id}")
                # Небольшая задержка между отправками сообщений
                await asyncio.sleep(0.5)
            except Exception as e:
                logging.error(f"Ошибка при отправке ежемесячного отчета пользователю {user.telegram_id}: {e}")
        
        logging.info("Ежемесячный отчет успешно отправлен всем пользователям")
    except Exception as e:
        logging.error(f"Ошибка при отправке ежемесячного отчета: {e}")

# Функция для запуска планировщика
async def start_scheduler():
    """Запуск планировщика задач"""
    try:
        # Создаем экземпляр планировщика
        scheduler = AsyncIOScheduler()
        
        # Добавляем задачи в планировщик
        
        # Ежедневный отчет в 10:00
        scheduler.add_job(send_daily_report, 'cron', hour=10, minute=0)
        
        # Еженедельный отчет в понедельник в 10:30
        scheduler.add_job(send_weekly_report, 'cron', day_of_week='mon', hour=10, minute=30)
        
        # Ежемесячный отчет первого числа каждого месяца в 11:00
        scheduler.add_job(send_monthly_report, 'cron', day=1, hour=11, minute=0)
        
        # Запускаем планировщик
        scheduler.start()
        logging.info("Планировщик задач запущен")
        
        # Бесконечный цикл для поддержания работы планировщика
        while True:
            await asyncio.sleep(1)
    
    except Exception as e:
        logging.error(f"Ошибка при запуске планировщика: {e}")

# Точка входа для запуска планировщика
if __name__ == "__main__":
    asyncio.run(start_scheduler()) 