import requests
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import YANDEX_METRIKA_TOKEN, YANDEX_METRIKA_COUNTER_ID

# Базовый URL API Яндекс Метрики
BASE_URL = "https://api-metrika.yandex.net/stat/v1/data"

def get_metrika_stats(date1: str, date2: str, metrics: List[str], dimensions: Optional[List[str]] = None, 
                     filters: Optional[str] = None, sort: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    """
    Получает статистику из Яндекс Метрики
    
    Args:
        date1: Начальная дата (YYYY-MM-DD)
        date2: Конечная дата (YYYY-MM-DD)
        metrics: Список метрик для получения
        dimensions: Список измерений для группировки (опционально)
        filters: Фильтры (опционально)
        sort: Сортировка (опционально)
        limit: Максимальное количество строк (опционально, по умолчанию 100)
        
    Returns:
        Словарь со статистикой
    """
    try:
        # Параметры запроса
        params = {
            "ids": YANDEX_METRIKA_COUNTER_ID,
            "date1": date1,
            "date2": date2,
            "metrics": ",".join(metrics),
            "limit": limit
        }
        
        # Добавляем опциональные параметры
        if dimensions:
            params["dimensions"] = ",".join(dimensions)
        if filters:
            params["filters"] = filters
        if sort:
            params["sort"] = sort
        
        # Заголовки запроса
        headers = {
            "Authorization": f"OAuth {YANDEX_METRIKA_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Выполняем запрос
        response = requests.get(BASE_URL, params=params, headers=headers)
        
        # Проверяем ответ
        if response.status_code != 200:
            print(f"Ошибка при запросе к API Яндекс Метрики: {response.status_code}")
            print(response.text)
            return {"error": f"API error: {response.status_code}", "details": response.text}
        
        # Парсим JSON
        return response.json()
    except Exception as e:
        print(f"Ошибка при получении статистики из Яндекс Метрики: {e}")
        return {"error": str(e)}

def get_daily_report() -> str:
    """
    Формирует ежедневный отчет о посещаемости сайта
    
    Returns:
        Строка с отчетом
    """
    try:
        # Дата вчерашнего дня
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Получаем основные метрики за вчерашний день
        stats = get_metrika_stats(
            date1=yesterday,
            date2=yesterday,
            metrics=["ym:s:visits", "ym:s:users", "ym:s:pageviews", "ym:s:bounceRate", "ym:s:avgVisitDurationSeconds"]
        )
        
        if "error" in stats:
            return f"Ошибка при получении отчета: {stats['error']}"
        
        # Вытаскиваем данные
        totals = stats.get("totals", [0, 0, 0, 0, 0])
        
        visits = totals[0]
        users = totals[1]
        pageviews = totals[2]
        bounce_rate = totals[3]
        avg_duration = totals[4]
        
        # Форматируем время в минуты и секунды
        minutes = int(avg_duration // 60)
        seconds = int(avg_duration % 60)
        
        # Получаем топ-5 источников трафика
        sources = get_metrika_stats(
            date1=yesterday,
            date2=yesterday,
            metrics=["ym:s:visits"],
            dimensions=["ym:s:trafficSource"],
            sort="-ym:s:visits",
            limit=5
        )
        
        # Формируем отчет
        report = f"📊 Отчет по Яндекс Метрике за {yesterday}\n\n"
        report += f"👥 Посетители: {users}\n"
        report += f"🔄 Визиты: {visits}\n"
        report += f"👁️ Просмотры страниц: {pageviews}\n"
        report += f"↩️ Отказы: {bounce_rate:.2f}%\n"
        report += f"⏱️ Среднее время на сайте: {minutes} мин {seconds} сек\n\n"
        
        # Добавляем информацию об источниках трафика
        if "error" not in sources and "data" in sources:
            report += "🔍 Топ источники трафика:\n"
            for i, source in enumerate(sources["data"], 1):
                source_name = source["dimensions"][0]["name"]
                source_visits = source["metrics"][0]
                report += f"{i}. {source_name}: {source_visits} визитов\n"
        
        return report
    except Exception as e:
        print(f"Ошибка при формировании отчета: {e}")
        return f"Ошибка при формировании отчета: {e}"

def get_weekly_report() -> str:
    """
    Формирует еженедельный отчет о посещаемости сайта
    
    Returns:
        Строка с отчетом
    """
    try:
        # Даты: от недели назад до вчера
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Получаем метрики за неделю
        stats = get_metrika_stats(
            date1=week_ago,
            date2=yesterday,
            metrics=["ym:s:visits", "ym:s:users", "ym:s:pageviews", "ym:s:bounceRate", "ym:s:avgVisitDurationSeconds"],
            dimensions=["ym:s:date"]
        )
        
        if "error" in stats:
            return f"Ошибка при получении отчета: {stats['error']}"
        
        # Общие показатели за неделю
        totals = stats.get("totals", [0, 0, 0, 0, 0])
        
        total_visits = totals[0]
        total_users = totals[1]
        total_pageviews = totals[2]
        avg_bounce_rate = totals[3]
        avg_duration = totals[4]
        
        # Форматируем время в минуты и секунды
        minutes = int(avg_duration // 60)
        seconds = int(avg_duration % 60)
        
        # Получаем топ-5 страниц
        pages = get_metrika_stats(
            date1=week_ago,
            date2=yesterday,
            metrics=["ym:s:pageviews"],
            dimensions=["ym:s:pageTitle"],
            sort="-ym:s:pageviews",
            limit=5
        )
        
        # Формируем отчет
        report = f"📈 Еженедельный отчет по Яндекс Метрике ({week_ago} - {yesterday})\n\n"
        report += f"👥 Всего посетителей: {total_users}\n"
        report += f"🔄 Всего визитов: {total_visits}\n"
        report += f"👁️ Всего просмотров: {total_pageviews}\n"
        report += f"↩️ Средний показатель отказов: {avg_bounce_rate:.2f}%\n"
        report += f"⏱️ Среднее время на сайте: {minutes} мин {seconds} сек\n\n"
        
        # Данные по дням
        if "data" in stats:
            report += "📅 Посещаемость по дням:\n"
            for day_data in stats["data"]:
                date_str = day_data["dimensions"][0]["name"]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m")
                day_visits = day_data["metrics"][0]
                report += f"{formatted_date}: {day_visits} визитов\n"
            
            report += "\n"
        
        # Топ страниц
        if "error" not in pages and "data" in pages:
            report += "📑 Топ страниц:\n"
            for i, page in enumerate(pages["data"], 1):
                page_title = page["dimensions"][0]["name"]
                page_views = page["metrics"][0]
                # Укорачиваем длинные заголовки
                if len(page_title) > 40:
                    page_title = page_title[:37] + "..."
                report += f"{i}. {page_title}: {page_views} просмотров\n"
        
        return report
    except Exception as e:
        print(f"Ошибка при формировании еженедельного отчета: {e}")
        return f"Ошибка при формировании еженедельного отчета: {e}"

def get_monthly_report() -> str:
    """
    Формирует ежемесячный отчет о посещаемости сайта
    
    Returns:
        Строка с отчетом
    """
    try:
        # Даты: от месяца назад до вчера
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Получаем метрики за месяц
        stats = get_metrika_stats(
            date1=month_ago,
            date2=yesterday,
            metrics=["ym:s:visits", "ym:s:users", "ym:s:pageviews", "ym:s:bounceRate", "ym:s:avgVisitDurationSeconds"]
        )
        
        if "error" in stats:
            return f"Ошибка при получении отчета: {stats['error']}"
        
        # Общие показатели за месяц
        totals = stats.get("totals", [0, 0, 0, 0, 0])
        
        total_visits = totals[0]
        total_users = totals[1]
        total_pageviews = totals[2]
        avg_bounce_rate = totals[3]
        avg_duration = totals[4]
        
        # Форматируем время в минуты и секунды
        minutes = int(avg_duration // 60)
        seconds = int(avg_duration % 60)
        
        # Получаем данные по устройствам
        devices = get_metrika_stats(
            date1=month_ago,
            date2=yesterday,
            metrics=["ym:s:visits"],
            dimensions=["ym:s:deviceCategory"],
            sort="-ym:s:visits"
        )
        
        # Получаем данные по регионам
        regions = get_metrika_stats(
            date1=month_ago,
            date2=yesterday,
            metrics=["ym:s:visits"],
            dimensions=["ym:s:regionCountry"],
            sort="-ym:s:visits",
            limit=5
        )
        
        # Формируем отчет
        report = f"📊 Ежемесячный отчет по Яндекс Метрике ({month_ago} - {yesterday})\n\n"
        report += f"👥 Всего уникальных посетителей: {total_users}\n"
        report += f"🔄 Всего визитов: {total_visits}\n"
        report += f"👁️ Всего просмотров страниц: {total_pageviews}\n"
        report += f"↩️ Средний показатель отказов: {avg_bounce_rate:.2f}%\n"
        report += f"⏱️ Среднее время на сайте: {minutes} мин {seconds} сек\n\n"
        
        # Данные по устройствам
        if "error" not in devices and "data" in devices:
            report += "📱 Визиты по устройствам:\n"
            for device in devices["data"]:
                device_name = device["dimensions"][0]["name"]
                device_visits = device["metrics"][0]
                device_percent = (device_visits / total_visits) * 100 if total_visits > 0 else 0
                report += f"{device_name}: {device_visits} ({device_percent:.1f}%)\n"
            
            report += "\n"
        
        # Данные по регионам
        if "error" not in regions and "data" in regions:
            report += "🌎 Топ регионов:\n"
            for region in regions["data"]:
                region_name = region["dimensions"][0]["name"]
                region_visits = region["metrics"][0]
                region_percent = (region_visits / total_visits) * 100 if total_visits > 0 else 0
                report += f"{region_name}: {region_visits} ({region_percent:.1f}%)\n"
        
        return report
    except Exception as e:
        print(f"Ошибка при формировании ежемесячного отчета: {e}")
        return f"Ошибка при формировании ежемесячного отчета: {e}"

# Тестирование функций
if __name__ == "__main__":
    daily_report = get_daily_report()
    print(daily_report) 