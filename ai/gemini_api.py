import google.generativeai as genai
import sys
import os
import PIL.Image
from typing import List, Dict, Optional, Union, Any

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS_RESPONSE

# Инициализация клиента Gemini
genai.configure(api_key=GEMINI_API_KEY)

def get_text_response(prompt: str, system_prompt: Optional[str] = None) -> str:
    """
    Получает текстовый ответ от Gemini по текстовому запросу
    
    Args:
        prompt: Текст запроса
        system_prompt: Системный промпт (инструкции для модели)
        
    Returns:
        Текстовый ответ от модели
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        if system_prompt:
            chat = model.start_chat(history=[])
            response = chat.send_message(
                f"{system_prompt}\n\n{prompt}"
            )
        else:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        print(f"Ошибка при получении ответа от Gemini: {e}")
        return f"Ошибка при получении ответа от нейросети: {e}"

def get_response_with_images(prompt: str, image_paths: List[str], system_prompt: Optional[str] = None) -> str:
    """
    Получает ответ от Gemini по текстовому запросу с изображениями
    
    Args:
        prompt: Текст запроса
        image_paths: Список путей к изображениям
        system_prompt: Системный промпт (инструкции для модели)
        
    Returns:
        Текстовый ответ от модели
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Загружаем изображения
        images = [PIL.Image.open(image_path) for image_path in image_paths]
        
        # Формируем системный промпт при необходимости
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Отправляем запрос с изображениями
        response = model.generate_content([full_prompt, *images])
        
        return response.text
    except Exception as e:
        print(f"Ошибка при получении ответа от Gemini: {e}")
        return f"Ошибка при получении ответа от нейросети: {e}"

def analyze_document(document_text: str, question: Optional[str] = None) -> str:
    """
    Анализирует текстовый документ с помощью Gemini
    
    Args:
        document_text: Текст документа для анализа
        question: Вопрос о документе (опционально)
        
    Returns:
        Текстовый ответ от модели с анализом документа
    """
    try:
        prompt = f"Вот документ для анализа:\n\n{document_text}\n\n"
        
        if question:
            prompt += f"Вопрос: {question}"
        else:
            prompt += "Пожалуйста, проанализируйте этот документ, выделите основные идеи, ключевые моменты и предоставьте краткое резюме."
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        print(f"Ошибка при анализе документа: {e}")
        return f"Ошибка при анализе документа: {e}"

def analyze_image(image_path: str, question: Optional[str] = None) -> str:
    """
    Анализирует изображение с помощью Gemini
    
    Args:
        image_path: Путь к изображению
        question: Вопрос об изображении (опционально)
        
    Returns:
        Текстовый ответ от модели с анализом изображения
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Загружаем изображение
        image = PIL.Image.open(image_path)
        
        # Формируем запрос
        prompt = "Проанализируйте это изображение и опишите, что на нем."
        if question:
            prompt = f"Проанализируйте это изображение. {question}"
        
        # Отправляем запрос с изображением
        response = model.generate_content([prompt, image])
        
        return response.text
    except Exception as e:
        print(f"Ошибка при анализе изображения: {e}")
        return f"Ошибка при анализе изображения: {e}"

def generate_marketing_strategy(business_type: str, target_audience: str, goals: str, budget: Optional[str] = None) -> str:
    """
    Генерирует маркетинговую стратегию
    
    Args:
        business_type: Тип бизнеса
        target_audience: Целевая аудитория
        goals: Цели маркетинговой стратегии
        budget: Бюджет (опционально)
        
    Returns:
        Текстовый ответ от модели с маркетинговой стратегией
    """
    try:
        system_prompt = "Вы опытный маркетолог-стратег с 20-летним опытом разработки успешных маркетинговых кампаний для разных видов бизнеса. Создавайте детальные, практические маркетинговые стратегии, которые можно сразу реализовать."
        
        prompt = f"Разработайте маркетинговую стратегию для {business_type}.\n\n"
        prompt += f"Целевая аудитория: {target_audience}\n"
        prompt += f"Цели: {goals}\n"
        
        if budget:
            prompt += f"Бюджет: {budget}\n"
        
        prompt += "\nСтратегия должна включать:\n"
        prompt += "1. Краткое резюме стратегии\n"
        prompt += "2. Анализ целевой аудитории\n"
        prompt += "3. Основные каналы продвижения\n"
        prompt += "4. Конкретные тактики для каждого канала\n"
        prompt += "5. Предложения по контент-плану\n"
        prompt += "6. Ключевые метрики для отслеживания эффективности\n"
        prompt += "7. Примерный план действий на 3 месяца\n"
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        chat = model.start_chat(history=[])
        response = chat.send_message(
            f"{system_prompt}\n\n{prompt}"
        )
            
        return response.text
    except Exception as e:
        print(f"Ошибка при генерации маркетинговой стратегии: {e}")
        return f"Ошибка при генерации маркетинговой стратегии: {e}"

def analyze_competitor(competitor_name: str, industry: str) -> str:
    """
    Анализирует конкурента
    
    Args:
        competitor_name: Название компании-конкурента
        industry: Отрасль
        
    Returns:
        Текстовый ответ от модели с анализом конкурента
    """
    try:
        system_prompt = "Вы опытный бизнес-аналитик, специализирующийся на конкурентном анализе. У вас есть знания о компаниях и рыночных тенденциях до января 2023 года."
        
        prompt = f"Проведите конкурентный анализ компании {competitor_name} в отрасли {industry}.\n\n"
        prompt += "Пожалуйста, включите в анализ:\n"
        prompt += "1. Общее описание компании и ее позиционирование\n"
        prompt += "2. Основные продукты/услуги\n"
        prompt += "3. Маркетинговые стратегии и каналы продвижения\n"
        prompt += "4. Сильные и слабые стороны\n"
        prompt += "5. Возможности для конкуренции с этой компанией\n"
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        chat = model.start_chat(history=[])
        response = chat.send_message(
            f"{system_prompt}\n\n{prompt}"
        )
            
        return response.text
    except Exception as e:
        print(f"Ошибка при анализе конкурента: {e}")
        return f"Ошибка при анализе конкурента: {e}" 