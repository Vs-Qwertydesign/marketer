import anthropic
import sys
import os
import base64
import mimetypes
from typing import List, Dict, Optional, Union, Any

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS_RESPONSE

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

def get_text_response(prompt: str, system_prompt: Optional[str] = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Получает текстовый ответ от Claude по текстовому запросу
    
    Args:
        prompt: Текст запроса
        system_prompt: Системный промпт (инструкции для модели)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текстовый ответ от модели
    """
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=system_prompt
        )
        return message.content[0].text
    except Exception as e:
        print(f"Ошибка при получении ответа от Claude: {e}")
        return f"Ошибка при получении ответа от нейросети: {e}"

def get_response_with_images(prompt: str, image_paths: List[str], system_prompt: Optional[str] = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Получает ответ от Claude по текстовому запросу с изображениями
    
    Args:
        prompt: Текст запроса
        image_paths: Список путей к изображениям
        system_prompt: Системный промпт (инструкции для модели)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текстовый ответ от модели
    """
    try:
        # Подготовка контента с изображениями
        content = []
        
        # Добавляем изображения
        for image_path in image_paths:
            content.append(create_image_content(image_path))
        
        # Добавляем текст запроса
        content.append({"type": "text", "text": prompt})
        
        # Отправляем запрос
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": content}
            ],
            system=system_prompt
        )
        return message.content[0].text
    except Exception as e:
        print(f"Ошибка при получении ответа от Claude: {e}")
        return f"Ошибка при получении ответа от нейросети: {e}"

def analyze_document(document_text: str, question: Optional[str] = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Анализирует текстовый документ с помощью Claude
    
    Args:
        document_text: Текст документа для анализа
        question: Вопрос о документе (опционально)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текстовый ответ от модели с анализом документа
    """
    try:
        prompt = f"Вот документ для анализа:\n\n{document_text}\n\n"
        
        if question:
            prompt += f"Вопрос: {question}"
        else:
            prompt += "Пожалуйста, проанализируйте этот документ, выделите основные идеи, ключевые моменты и предоставьте краткое резюме."
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Ошибка при анализе документа: {e}")
        return f"Ошибка при анализе документа: {e}"

def generate_project_ideas(field: str, goals: str, constraints: Optional[str] = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Генерирует идеи для маркетингового проекта
    
    Args:
        field: Область маркетинга или ниша
        goals: Цели проекта
        constraints: Ограничения проекта (опционально)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текстовый ответ от модели с идеями для проекта
    """
    try:
        system_prompt = "Вы опытный маркетолог-стратег с большим опытом работы в различных нишах. Ваша задача - генерировать креативные и эффективные идеи для маркетинговых проектов."
        
        prompt = f"Предложите идеи для маркетингового проекта в области {field}.\n\nЦели проекта: {goals}"
        
        if constraints:
            prompt += f"\n\nОграничения: {constraints}"
        
        prompt += "\n\nПожалуйста, предложите 3-5 конкретных и реализуемых идей. Для каждой идеи укажите:\n1. Краткое описание\n2. Потенциальные результаты\n3. Ресурсы, необходимые для реализации\n4. Примерные сроки\n5. Риски и как их минимизировать"
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=system_prompt
        )
        return message.content[0].text
    except Exception as e:
        print(f"Ошибка при генерации идей для проекта: {e}")
        return f"Ошибка при генерации идей для проекта: {e}"

def analyze_market_trends(industry: str, question: Optional[str] = None, max_tokens: int = MAX_TOKENS_RESPONSE) -> str:
    """
    Анализирует тренды рынка в указанной отрасли
    
    Args:
        industry: Отрасль для анализа
        question: Конкретный вопрос о тренде (опционально)
        max_tokens: Максимальное количество токенов в ответе
        
    Returns:
        Текстовый ответ от модели с анализом трендов
    """
    try:
        system_prompt = "Вы опытный аналитик рынка с глубоким пониманием различных отраслей. У вас есть знания о рыночных тенденциях до января 2023 года. Объясняйте тренды ясно и подробно."
        
        prompt = f"Проанализируйте текущие тренды в отрасли {industry}."
        
        if question:
            prompt += f"\n\nКонкретно интересует следующий вопрос: {question}"
        else:
            prompt += "\n\nОпишите:\n1. Основные текущие тренды\n2. Потенциальные возможности для бизнеса\n3. Риски и вызовы\n4. Прогнозы на ближайшие 1-2 года"
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=system_prompt
        )
        return message.content[0].text
    except Exception as e:
        print(f"Ошибка при анализе трендов рынка: {e}")
        return f"Ошибка при анализе трендов рынка: {e}" 