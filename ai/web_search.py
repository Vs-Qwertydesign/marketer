import requests
import json
import sys
import os
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SERP_API_KEY

def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Выполняет поиск в интернете с помощью SerpAPI
    
    Args:
        query: Поисковый запрос
        num_results: Количество результатов (максимум 10)
        
    Returns:
        Список результатов поиска
    """
    try:
        # Параметры запроса
        params = {
            "engine": "google",
            "q": query,
            "api_key": SERP_API_KEY,
            "num": min(num_results, 10)  # Ограничиваем до 10 результатов
        }
        
        # Отправляем запрос
        response = requests.get("https://serpapi.com/search", params=params)
        
        # Проверяем успешность запроса
        if response.status_code != 200:
            print(f"Ошибка при выполнении поискового запроса: {response.status_code}")
            return []
        
        # Преобразуем ответ в JSON
        data = response.json()
        
        # Проверяем наличие результатов
        if "organic_results" not in data:
            print("Результаты не найдены")
            return []
        
        # Формируем список результатов
        results = []
        for result in data["organic_results"][:num_results]:
            results.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return results
    except Exception as e:
        print(f"Ошибка при выполнении поискового запроса: {e}")
        return []

def fetch_webpage_content(url: str, max_length: int = 5000) -> Optional[str]:
    """
    Получает содержимое веб-страницы
    
    Args:
        url: URL страницы
        max_length: Максимальная длина возвращаемого текста
        
    Returns:
        Текстовое содержимое страницы или None в случае ошибки
    """
    try:
        # Отправляем запрос
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Проверяем успешность запроса
        if response.status_code != 200:
            print(f"Ошибка при получении содержимого страницы: {response.status_code}")
            return None
        
        # Получаем содержимое страницы
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Удаляем скрипты, стили и другие ненужные элементы
        for script in soup(["script", "style", "meta", "noscript", "head", "footer"]):
            script.extract()
        
        # Получаем текст
        text = soup.get_text(separator='\n')
        
        # Чистим текст от лишних пробелов и переносов строк
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Ограничиваем длину текста
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    except Exception as e:
        print(f"Ошибка при получении содержимого страницы: {e}")
        return None

def research_topic(topic: str, depth: int = 3) -> Dict[str, Any]:
    """
    Проводит исследование по заданной теме
    
    Args:
        topic: Тема для исследования
        depth: Глубина исследования (количество статей для анализа)
        
    Returns:
        Словарь с результатами исследования
    """
    try:
        # Выполняем поиск по теме
        search_results = search_web(topic, num_results=depth)
        
        # Проверяем наличие результатов
        if not search_results:
            return {
                "success": False,
                "message": "Результаты не найдены",
                "data": []
            }
        
        # Анализируем каждый результат
        research_data = []
        for result in search_results:
            # Получаем содержимое страницы
            content = fetch_webpage_content(result["link"])
            
            if content:
                # Добавляем информацию в результаты
                research_data.append({
                    "title": result["title"],
                    "url": result["link"],
                    "snippet": result["snippet"],
                    "content_summary": content[:500] + "..." if len(content) > 500 else content
                })
        
        return {
            "success": True,
            "message": f"Найдено {len(research_data)} источников информации",
            "data": research_data
        }
    except Exception as e:
        print(f"Ошибка при проведении исследования: {e}")
        return {
            "success": False,
            "message": str(e),
            "data": []
        }

def search_and_summarize(query: str, model: str = "claude") -> str:
    """
    Выполняет поиск и суммирует результаты с помощью ИИ
    
    Args:
        query: Поисковый запрос
        model: Модель для суммирования ('claude' или 'gemini')
        
    Returns:
        Суммированный результат
    """
    try:
        # Выполняем поиск
        search_results = search_web(query, num_results=5)
        
        if not search_results:
            return "Информация по запросу не найдена."
        
        # Формируем текст для суммирования
        summary_text = f"Результаты поиска по запросу: '{query}'\n\n"
        
        for i, result in enumerate(search_results, 1):
            summary_text += f"{i}. {result['title']}\n"
            summary_text += f"   URL: {result['link']}\n"
            summary_text += f"   Аннотация: {result['snippet']}\n\n"
            
            # Получаем содержимое страницы (если есть)
            content = fetch_webpage_content(result["link"], max_length=3000)
            if content:
                summary_text += f"   Содержание: {content[:300]}...\n\n"
        
        # Выбираем модель для суммирования
        if model.lower() == "claude":
            from ai.claude_api import get_text_response
            
            system_prompt = "Вы опытный исследователь и аналитик информации. Ваша задача - суммировать результаты поиска в интернете и выделить самую важную информацию."
            prompt = f"Проанализируйте следующие результаты поиска по запросу '{query}' и создайте краткое, но информативное резюме. Сфокусируйтесь на ключевых фактах, общих темах и выводах.\n\n{summary_text}"
            
            summary = get_text_response(prompt, system_prompt)
        else:  # gemini
            from ai.gemini_api import get_text_response
            
            system_prompt = "Вы опытный исследователь и аналитик информации. Ваша задача - суммировать результаты поиска в интернете и выделить самую важную информацию."
            prompt = f"Проанализируйте следующие результаты поиска по запросу '{query}' и создайте краткое, но информативное резюме. Сфокусируйтесь на ключевых фактах, общих темах и выводах.\n\n{summary_text}"
            
            summary = get_text_response(prompt, system_prompt)
        
        return summary
    except Exception as e:
        print(f"Ошибка при поиске и суммировании: {e}")
        return f"Произошла ошибка при поиске информации: {e}" 