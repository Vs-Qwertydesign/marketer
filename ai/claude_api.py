import anthropic
import sys
import os
import base64
import mimetypes
from typing import List, Dict, Optional, Union, Any
import httpx
import logging
import json

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS_RESPONSE, GEMINI_API_KEY
from ai.gemini_api import get_text_response as gemini_get_text_response

# Инициализация клиента Claude
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def encode_image_to_base64(image_path: str) -> str:
    """Кодирует изображение в base64 строку"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_image_content(image_path: str) -> Dict[str, Any]:
    """Создает содержимое с изображением для отправки в Claude"""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    if not mime_type.startswith('image/'):
        raise ValueError(f"Файл {image_path} не является изображением")
    
    base64_image = encode_image_to_base64(image_path)
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": mime_type,
            "data": base64_image
        }
    }

def get_text_response(user_message: str, system_prompt: str = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Получает ответ от модели Claude на текстовый запрос
    
    Args:
        user_message: Сообщение пользователя
        system_prompt: Системный промпт для модели (опционально)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Ответ модели
    """
    try:
        # Если system_prompt не указан, используем дефолтное значение
        if not system_prompt:
            system_prompt = "Вы полезный ассистент, который отвечает на вопросы пользователя. Ваши ответы должны быть информативными и точными."
        
        # Создаем сообщение
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        
        # Возвращаем текст ответа
        return response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка при получении ответа от Claude: {e}")
        
        # Если произошла ошибка, пробуем использовать Gemini API
        try:
            logging.info("Пробуем использовать Gemini API для получения ответа")
            gemini_response = gemini_get_text_response(user_message, system_prompt)
            return gemini_response
        except Exception as gemini_error:
            logging.error(f"Ошибка при использовании Gemini API: {gemini_error}")
            return f"Произошла ошибка при обработке вашего запроса: {e}"

def get_response_with_images(user_message: str, image_paths: List[str], system_prompt: str = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Получает ответ от модели Claude на запрос с изображениями
    
    Args:
        user_message: Сообщение пользователя
        image_paths: Список путей к изображениям
        system_prompt: Системный промпт для модели (опционально)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Ответ модели
    """
    try:
        # Если system_prompt не указан, используем дефолтное значение
        if not system_prompt:
            system_prompt = "Вы полезный ассистент, который анализирует изображения и отвечает на вопросы пользователя. Ваши ответы должны быть информативными и точными."
        
        # Создаем сообщение
        messages = [{"role": "user", "content": [{"type": "text", "text": user_message}]}]
        
        # Добавляем изображения
        for image_path in image_paths:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Добавляем изображение в сообщение
            messages[0]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": image_data.hex()
                }
            })
        
        # Отправляем запрос
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )
        
        # Возвращаем текст ответа
        return response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка при получении ответа с изображениями от Claude: {e}")
        
        # Если произошла ошибка, пробуем использовать Gemini API
        try:
            logging.info("Пробуем использовать Gemini API для анализа изображений")
            from ai.gemini_api import analyze_image
            # Используем первое изображение для анализа (если есть)
            if image_paths:
                gemini_response = analyze_image(image_paths[0], user_message)
                return gemini_response
            else:
                return f"Произошла ошибка при обработке изображений: {e}"
        except Exception as gemini_error:
            logging.error(f"Ошибка при использовании Gemini API для изображений: {gemini_error}")
            return f"Произошла ошибка при обработке вашего запроса с изображениями: {e}"

def analyze_document(text: str, question: Optional[str] = None) -> str:
    """
    Анализирует документ с помощью Claude
    
    Args:
        text: Текст документа
        question: Вопрос о документе (опционально)
        
    Returns:
        Результат анализа
    """
    try:
        # Подготавливаем промпт
        if question:
            prompt = f"Вот документ для анализа:\n\n{text}\n\nВопрос: {question}\n\nПожалуйста, дайте подробный ответ на вопрос на основе содержимого документа."
        else:
            prompt = f"Вот документ для анализа:\n\n{text}\n\nПожалуйста, проанализируйте его и выделите основные идеи, ключевые моменты и важные детали."
        
        # Получаем ответ от модели
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_RESPONSE,
            system="Вы эксперт по анализу документов. Ваша задача - анализировать документы и отвечать на вопросы о них.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Возвращаем ответ
        return response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка при анализе документа: {e}")
        
        # Если произошла ошибка, пробуем использовать Gemini API
        try:
            logging.info("Пробуем использовать Gemini API для анализа документа")
            gemini_response = gemini_get_text_response(
                f"Анализ документа:\n\n{text}\n\n{'Вопрос: ' + question if question else 'Проанализируйте документ и выделите основные идеи, ключевые моменты и важные детали.'}",
                "Вы эксперт по анализу документов. Ваша задача - анализировать документы и отвечать на вопросы о них."
            )
            return gemini_response
        except Exception as gemini_error:
            logging.error(f"Ошибка при использовании Gemini API для анализа документа: {gemini_error}")
            return f"Произошла ошибка при анализе документа: {e}"

def generate_project_ideas(field: str, goals: str, constraints: Optional[str] = None) -> str:
    """
    Генерирует идеи для проекта с помощью Claude
    
    Args:
        field: Область проекта
        goals: Цели проекта
        constraints: Ограничения проекта (опционально)
        
    Returns:
        Сгенерированные идеи
    """
    try:
        # Подготавливаем промпт
        if constraints:
            prompt = f"Генерация идей для проекта в области: {field}.\n\nЦели проекта: {goals}.\n\nОграничения: {constraints}.\n\nПредложите 5-7 креативных и практичных идей для маркетингового проекта, учитывая указанные цели и ограничения."
        else:
            prompt = f"Генерация идей для проекта в области: {field}.\n\nЦели проекта: {goals}.\n\nПредложите 5-7 креативных и практичных идей для маркетингового проекта, учитывая указанные цели."
        
        # Получаем ответ от модели
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_RESPONSE,
            system="Вы креативный маркетолог с опытом генерации идей для проектов в различных областях. Ваша задача - предложить креативные и практичные идеи для маркетинговых проектов, учитывая цели и ограничения.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Возвращаем ответ
        return response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка при генерации идей для проекта: {e}")
        
        # Если произошла ошибка, пробуем использовать Gemini API
        try:
            logging.info("Пробуем использовать Gemini API для генерации идей")
            gemini_response = gemini_get_text_response(
                prompt,
                "Вы креативный маркетолог с опытом генерации идей для проектов в различных областях. Ваша задача - предложить креативные и практичные идеи для маркетинговых проектов, учитывая цели и ограничения."
            )
            return gemini_response
        except Exception as gemini_error:
            logging.error(f"Ошибка при использовании Gemini API для генерации идей: {gemini_error}")
            return f"Произошла ошибка при генерации идей для проекта: {e}"

def analyze_market_trends(industry: str) -> str:
    """
    Анализирует рыночные тренды в указанной отрасли с помощью Claude
    
    Args:
        industry: Отрасль для анализа
        
    Returns:
        Результат анализа
    """
    try:
        # Подготавливаем промпт
        prompt = f"Анализ рыночных трендов в отрасли: {industry}.\n\nПожалуйста, проанализируйте текущие тренды, тенденции и перспективы развития в этой отрасли. Включите информацию о ключевых игроках, инновациях, потребительских предпочтениях и прогнозах на ближайшие 1-2 года."
        
        # Получаем ответ от модели
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS_RESPONSE,
            system="Вы эксперт по рыночным исследованиям и анализу трендов. Ваша задача - предоставить комплексный анализ трендов и тенденций в указанной отрасли, основываясь на ваших знаниях о рынке.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Возвращаем ответ
        return response.content[0].text
    except Exception as e:
        logging.error(f"Ошибка при анализе трендов рынка: {e}")
        
        # Если произошла ошибка, пробуем использовать Gemini API
        try:
            logging.info("Пробуем использовать Gemini API для анализа рыночных трендов")
            gemini_response = gemini_get_text_response(
                prompt,
                "Вы эксперт по рыночным исследованиям и анализу трендов. Ваша задача - предоставить комплексный анализ трендов и тенденций в указанной отрасли, основываясь на ваших знаниях о рынке."
            )
            return gemini_response
        except Exception as gemini_error:
            logging.error(f"Ошибка при использовании Gemini API для анализа трендов: {gemini_error}")
            return f"Произошла ошибка при анализе трендов рынка: {e}" 