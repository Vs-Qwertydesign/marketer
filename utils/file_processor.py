import os
import sys
import json
import docx
import pydub
import pytesseract
import PyPDF2
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple
import io
import re
from elevenlabs import client
from elevenlabs.client import ElevenLabs

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MAX_FILE_SIZE_MB, ELEVEN_LABS_API_KEY
from ai.claude_api import analyze_document
from ai.gemini_api import analyze_image

# Максимальный размер файла в байтах
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

# Инициализация ElevenLabs клиента
eleven_labs_client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

def save_file(file_data: bytes, file_name: str, directory: str = "temp_files") -> str:
    """
    Сохраняет файл на диск
    
    Args:
        file_data: Бинарные данные файла
        file_name: Имя файла
        directory: Директория для сохранения
        
    Returns:
        Путь к сохраненному файлу
    """
    try:
        # Проверяем, существует ли директория
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Сохраняем файл
        file_path = os.path.join(directory, file_name)
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        return file_path
    except Exception as e:
        print(f"Ошибка при сохранении файла: {e}")
        return ""

def get_file_type(file_path: str) -> str:
    """
    Определяет тип файла по расширению
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Тип файла (text, image, audio, document, unknown)
    """
    # Получаем расширение файла
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Текстовые файлы
    if ext in [".txt", ".csv", ".json", ".xml", ".html", ".md"]:
        return "text"
    
    # Изображения
    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]:
        return "image"
    
    # Аудио
    elif ext in [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]:
        return "audio"
    
    # Документы
    elif ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
        return "document"
    
    # Неизвестный тип
    else:
        return "unknown"

def check_file_size(file_path: str) -> bool:
    """
    Проверяет размер файла
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        True, если размер файла не превышает максимальный, иначе False
    """
    # Получаем размер файла
    file_size = os.path.getsize(file_path)
    
    # Проверяем размер
    return file_size <= MAX_FILE_SIZE

def extract_text_from_txt(file_path: str) -> str:
    """
    Извлекает текст из текстового файла
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Извлеченный текст
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Пробуем другие кодировки
        try:
            with open(file_path, "r", encoding="cp1251") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except Exception as e:
                print(f"Ошибка при чтении текстового файла: {e}")
                return ""
    except Exception as e:
        print(f"Ошибка при чтении текстового файла: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """
    Извлекает текст из файла .docx
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Извлеченный текст
    """
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Ошибка при чтении файла docx: {e}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    """
    Извлекает текст из файла PDF
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Извлеченный текст
    """
    try:
        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Ошибка при чтении файла PDF: {e}")
        return ""

def extract_text_from_image(file_path: str) -> str:
    """
    Извлекает текст из изображения с помощью OCR
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Извлеченный текст
    """
    try:
        # Открываем изображение
        image = Image.open(file_path)
        
        # Применяем OCR
        text = pytesseract.image_to_string(image, lang='rus+eng')
        
        return text
    except Exception as e:
        print(f"Ошибка при извлечении текста из изображения: {e}")
        return ""

def transcribe_audio(file_path: str, language: str = None) -> str:
    """
    Преобразует аудио в текст с использованием Eleven Labs API
    
    Args:
        file_path: Путь к файлу
        language: Код языка (опционально, авто-определение если не указан)
        
    Returns:
        Транскрибированный текст
    """
    try:
        # Проверяем размер файла
        if not check_file_size(file_path):
            return f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE_MB} МБ."
        
        # Конвертируем в формат MP3, если нужно
        audio_format = os.path.splitext(file_path)[1].lower()
        
        # Если файл не MP3, конвертируем его
        audio_path = file_path
        if audio_format != ".mp3":
            sound = pydub.AudioSegment.from_file(file_path)
            audio_path = file_path + ".mp3"
            sound.export(audio_path, format="mp3")
        
        # Открываем аудио файл
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Параметры запроса
        params = {}
        if language:
            params["language"] = language
            
        # Отправляем запрос на транскрибацию
        response = eleven_labs_client.speech_to_text.convert(
            audio=audio_data,
            **params
        )
        
        # Удаляем временный файл, если он был создан
        if audio_path != file_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        # Возвращаем транскрибированный текст
        return response.text
    except Exception as e:
        print(f"Ошибка при транскрибации аудио: {e}")
        return f"Ошибка при обработке аудио файла: {e}"

def process_file(file_path: str) -> Dict[str, Any]:
    """
    Обрабатывает файл в зависимости от его типа
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        Словарь с результатами обработки файла
    """
    try:
        # Проверяем размер файла
        if not check_file_size(file_path):
            return {
                "success": False,
                "message": f"Размер файла превышает максимально допустимый ({MAX_FILE_SIZE_MB} МБ)",
                "text": "",
                "file_type": ""
            }
        
        # Определяем тип файла
        file_type = get_file_type(file_path)
        
        # Обрабатываем файл в зависимости от типа
        text = ""
        if file_type == "text":
            text = extract_text_from_txt(file_path)
        elif file_type == "document":
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif ext in [".docx", ".doc"]:
                text = extract_text_from_docx(file_path)
        elif file_type == "image":
            # Для изображений возвращаем путь, анализировать будем отдельно
            return {
                "success": True,
                "message": "Изображение успешно загружено",
                "text": "",
                "file_type": file_type,
                "file_path": file_path
            }
        elif file_type == "audio":
            # Для аудио возвращаем путь, транскрибировать будем отдельно
            return {
                "success": True,
                "message": "Аудио файл успешно загружен",
                "text": "",
                "file_type": file_type,
                "file_path": file_path
            }
        
        # Проверяем, извлекли ли мы текст
        if text:
            return {
                "success": True,
                "message": "Файл успешно обработан",
                "text": text,
                "file_type": file_type
            }
        else:
            return {
                "success": False,
                "message": "Не удалось извлечь текст из файла",
                "text": "",
                "file_type": file_type
            }
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return {
            "success": False,
            "message": f"Ошибка при обработке файла: {e}",
            "text": "",
            "file_type": ""
        }

def analyze_file_with_ai(file_path: str, question: Optional[str] = None) -> str:
    """
    Анализирует файл с помощью ИИ
    
    Args:
        file_path: Путь к файлу
        question: Вопрос о содержимом файла (опционально)
        
    Returns:
        Результат анализа
    """
    try:
        # Определяем тип файла
        file_type = get_file_type(file_path)
        
        # Обрабатываем файл в зависимости от типа
        if file_type in ["text", "document"]:
            # Извлекаем текст
            text = ""
            ext = os.path.splitext(file_path)[1].lower()
            if file_type == "text":
                text = extract_text_from_txt(file_path)
            elif ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif ext in [".docx", ".doc"]:
                text = extract_text_from_docx(file_path)
            
            # Анализируем текст с помощью Claude
            if text:
                return analyze_document(text, question)
            else:
                return "Не удалось извлечь текст из файла."
        
        elif file_type == "image":
            # Анализируем изображение с помощью Gemini
            return analyze_image(file_path, question)
        
        elif file_type == "audio":
            # Транскрибируем аудио и затем анализируем текст
            transcription = transcribe_audio(file_path)
            if transcription and not transcription.startswith("Ошибка"):
                # Добавляем префикс, чтобы указать, что это транскрипция
                analysis_text = f"Транскрипция аудио:\n\n{transcription}\n\n"
                
                # Если есть вопрос, анализируем с его помощью
                if question:
                    analysis = analyze_document(transcription, question)
                    analysis_text += f"Анализ транскрипции:\n\n{analysis}"
                    return analysis_text
                else:
                    return analysis_text
            else:
                return transcription
        
        else:
            return f"Анализ файлов типа {file_type} не поддерживается."
    
    except Exception as e:
        print(f"Ошибка при анализе файла: {e}")
        return f"Ошибка при анализе файла: {e}" 