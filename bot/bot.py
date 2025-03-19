import asyncio
import os
import sys
import logging
import uuid
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from contextlib import suppress

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BOT_TOKEN
from database.db_operations import get_or_create_user, create_project, get_projects_by_user, get_active_conversation, create_conversation, add_message
from utils.file_processor import save_file, process_file, analyze_file_with_ai, transcribe_audio
from ai.claude_api import get_text_response, get_response_with_images, generate_project_ideas, analyze_market_trends
from ai.gemini_api import get_text_response as gemini_get_text_response
from ai.web_search import search_and_summarize
from utils.yandex_metrika import get_daily_report, get_weekly_report, get_monthly_report

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# Определение состояний для FSM
class States(StatesGroup):
    main = State()
    waiting_project_name = State()
    waiting_project_description = State()
    waiting_document_question = State()
    waiting_search_query = State()
    waiting_market_industry = State()
    waiting_idea_field = State()
    waiting_idea_goals = State()
    waiting_idea_constraints = State()
    waiting_audio_language = State()

# Инициализация бота
async def bot_startup():
    """Инициализация бота при запуске"""
    logging.info("Бот запущен")
    
    # Создаем временную директорию для файлов, если её нет
    if not os.path.exists("temp_files"):
        os.makedirs("temp_files")

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Получаем или создаем пользователя
    user = get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    # Отправляем приветственное сообщение
    await message.answer(
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        "Я ваш персональный помощник маркетолога. Я могу помочь вам с различными маркетинговыми задачами:\n"
        "• Управление проектами\n"
        "• Анализ документов и изображений\n"
        "• Транскрибация аудио\n"
        "• Поиск информации в интернете\n"
        "• Генерация идей для проектов\n"
        "• Анализ рыночных трендов\n"
        "• Отчеты по Яндекс.Метрике\n\n"
        "Используйте команду /help для получения списка доступных команд."
    )
    
    # Устанавливаем состояние основного меню
    await state.set_state(States.main)

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 Список доступных команд:\n\n"
        "/start - Запустить бота\n"
        "/help - Показать список команд\n"
        "/project - Создать новый проект\n"
        "/projects - Показать список ваших проектов\n"
        "/search - Поиск информации в интернете\n"
        "/ideas - Генерация идей для проекта\n"
        "/market - Анализ рыночных трендов\n"
        "/metrika - Получить отчет по Яндекс.Метрике\n\n"
        "Вы также можете отправить мне документ, изображение, аудио или просто задать вопрос."
    )
    await message.answer(help_text)

# Обработчик команды /project
@router.message(Command("project"))
async def cmd_project(message: Message, state: FSMContext):
    """Обработчик команды для создания нового проекта"""
    await message.answer("Введите название нового проекта:")
    await state.set_state(States.waiting_project_name)

# Обработчик ввода названия проекта
@router.message(States.waiting_project_name)
async def process_project_name(message: Message, state: FSMContext):
    """Обработка ввода названия проекта"""
    # Сохраняем название проекта
    await state.update_data(project_name=message.text)
    
    # Запрашиваем описание проекта
    await message.answer("Введите описание проекта (или введите '-' для пропуска):")
    await state.set_state(States.waiting_project_description)

# Обработчик ввода описания проекта
@router.message(States.waiting_project_description)
async def process_project_description(message: Message, state: FSMContext):
    """Обработка ввода описания проекта"""
    # Получаем данные из состояния
    data = await state.get_data()
    project_name = data.get("project_name")
    
    # Определяем описание
    description = message.text if message.text != "-" else None
    
    # Получаем пользователя
    user = get_or_create_user(telegram_id=message.from_user.id)
    
    # Создаем проект
    project_id = create_project(user.id, project_name, description)
    
    # Отправляем сообщение об успешном создании проекта
    await message.answer(
        f"✅ Проект '{project_name}' успешно создан!\n\n"
        f"Вы можете теперь работать с этим проектом, задавать вопросы или загружать документы."
    )
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)

# Обработчик команды /projects
@router.message(Command("projects"))
async def cmd_projects(message: Message):
    """Обработчик команды для просмотра списка проектов"""
    # Получаем пользователя
    user = get_or_create_user(telegram_id=message.from_user.id)
    
    # Получаем проекты пользователя
    projects = get_projects_by_user(user.id)
    
    if not projects:
        await message.answer("У вас пока нет проектов. Используйте команду /project, чтобы создать новый проект.")
        return
    
    # Формируем сообщение со списком проектов
    projects_text = "📁 Ваши проекты:\n\n"
    for i, project in enumerate(projects, 1):
        creation_date = project.created_at.strftime("%d.%m.%Y")
        projects_text += f"{i}. {project.name} (создан {creation_date})\n"
        projects_text += f"   Статус: {project.status}\n"
        if project.description:
            projects_text += f"   Описание: {project.description[:50]}{'...' if len(project.description) > 50 else ''}\n"
        projects_text += "\n"
    
    await message.answer(projects_text)

# Обработчик команды /search
@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """Обработчик команды для поиска информации"""
    await message.answer("Введите поисковый запрос:")
    await state.set_state(States.waiting_search_query)

# Обработчик ввода поискового запроса
@router.message(States.waiting_search_query)
async def process_search_query(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    query = message.text
    
    # Отправляем сообщение о начале поиска
    await message.answer(f"🔎 Ищу информацию по запросу: '{query}'...")
    
    # Выполняем поиск и получаем результат
    result = await asyncio.to_thread(search_and_summarize, query)
    
    # Отправляем результат
    await message.answer(result)
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)

# Обработчик команды /market
@router.message(Command("market"))
async def cmd_market(message: Message, state: FSMContext):
    """Обработчик команды для анализа рынка"""
    await message.answer("Введите отрасль или сферу бизнеса для анализа трендов:")
    await state.set_state(States.waiting_market_industry)

# Обработчик ввода отрасли для анализа рынка
@router.message(States.waiting_market_industry)
async def process_market_industry(message: Message, state: FSMContext):
    """Обработка ввода отрасли для анализа рынка"""
    industry = message.text
    
    # Отправляем сообщение о начале анализа
    await message.answer(f"📊 Анализирую тренды в отрасли '{industry}'...\nЭто может занять некоторое время.")
    
    # Получаем анализ трендов
    result = await asyncio.to_thread(analyze_market_trends, industry)
    
    # Отправляем результат
    await message.answer(result)
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)

# Обработчик команды /ideas
@router.message(Command("ideas"))
async def cmd_ideas(message: Message, state: FSMContext):
    """Обработчик команды для генерации идей"""
    await message.answer("Введите область или нишу для генерации идей (например, 'интернет-магазин одежды', 'мобильное приложение', 'B2B-услуги'):")
    await state.set_state(States.waiting_idea_field)

# Обработчик ввода области для генерации идей
@router.message(States.waiting_idea_field)
async def process_idea_field(message: Message, state: FSMContext):
    """Обработка ввода области для генерации идей"""
    # Сохраняем область
    await state.update_data(idea_field=message.text)
    
    # Запрашиваем цели
    await message.answer("Введите цели проекта (например, 'увеличение продаж', 'привлечение новой аудитории', 'выход на международный рынок'):")
    await state.set_state(States.waiting_idea_goals)

# Обработчик ввода целей для генерации идей
@router.message(States.waiting_idea_goals)
async def process_idea_goals(message: Message, state: FSMContext):
    """Обработка ввода целей для генерации идей"""
    # Сохраняем цели
    await state.update_data(idea_goals=message.text)
    
    # Запрашиваем ограничения
    await message.answer("Введите ограничения или особые требования проекта (или введите '-' для пропуска):")
    await state.set_state(States.waiting_idea_constraints)

# Обработчик ввода ограничений для генерации идей
@router.message(States.waiting_idea_constraints)
async def process_idea_constraints(message: Message, state: FSMContext):
    """Обработка ввода ограничений для генерации идей"""
    # Получаем данные из состояния
    data = await state.get_data()
    field = data.get("idea_field")
    goals = data.get("idea_goals")
    
    # Определяем ограничения
    constraints = message.text if message.text != "-" else None
    
    # Отправляем сообщение о начале генерации
    await message.answer(f"💡 Генерирую идеи для '{field}'...\nЭто может занять некоторое время.")
    
    # Генерируем идеи
    result = await asyncio.to_thread(generate_project_ideas, field, goals, constraints)
    
    # Отправляем результат
    await message.answer(result)
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)

# Обработчик команды /metrika
@router.message(Command("metrika"))
async def cmd_metrika(message: Message):
    """Обработчик команды для получения отчета по Яндекс.Метрике"""
    # Создаем кнопки для выбора типа отчета
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ежедневный отчет", callback_data="metrika_daily")],
        [InlineKeyboardButton(text="Еженедельный отчет", callback_data="metrika_weekly")],
        [InlineKeyboardButton(text="Ежемесячный отчет", callback_data="metrika_monthly")]
    ])
    
    await message.answer(
        "Выберите тип отчета по Яндекс.Метрике:",
        reply_markup=markup
    )

# Обработчик выбора типа отчета по Яндекс.Метрике
@router.callback_query(lambda c: c.data.startswith("metrika_"))
async def process_metrika_report(callback_query: CallbackQuery):
    """Обработка выбора типа отчета по Яндекс.Метрике"""
    report_type = callback_query.data.split("_")[1]
    
    # Отправляем сообщение о начале формирования отчета
    await callback_query.message.answer("📊 Формирую отчет по Яндекс.Метрике...")
    
    # Получаем отчет в зависимости от выбранного типа
    if report_type == "daily":
        report = await asyncio.to_thread(get_daily_report)
    elif report_type == "weekly":
        report = await asyncio.to_thread(get_weekly_report)
    elif report_type == "monthly":
        report = await asyncio.to_thread(get_monthly_report)
    else:
        report = "Неизвестный тип отчета"
    
    # Отправляем отчет
    await callback_query.message.answer(report)
    
    # Отвечаем на колбэк
    await callback_query.answer()

# Обработчик получения документа или фото
@router.message(lambda message: message.document or message.photo or message.voice or message.audio)
async def process_document(message: Message, state: FSMContext):
    """Обработчик получения документа, фото или аудио"""
    # Определяем тип файла и получаем его
    file_id = None
    file_name = None
    file_type = None
    
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_type = "document"
    elif message.photo:
        # Берем последнее (самое крупное) фото
        file_id = message.photo[-1].file_id
        # Генерируем имя для фото
        file_name = f"photo_{uuid.uuid4()}.jpg"
        file_type = "photo"
    elif message.voice:
        file_id = message.voice.file_id
        file_name = f"voice_{uuid.uuid4()}.ogg"
        file_type = "audio"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{uuid.uuid4()}.mp3"
        file_type = "audio"
    
    if not file_id:
        await message.answer("Не удалось получить файл.")
        return
    
    # Скачиваем файл
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_content = await bot.download_file(file_path)
    
    # Сохраняем файл
    saved_path = await asyncio.to_thread(save_file, file_content.read(), file_name)
    
    if not saved_path:
        await message.answer("Не удалось сохранить файл.")
        return
    
    # Обрабатываем файл в зависимости от типа
    if file_type == "audio":
        # Сохраняем путь к файлу в состоянии
        await state.update_data(audio_file_path=saved_path)
        
        # Предлагаем выбрать язык для транскрибации
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Русский", callback_data="audio_lang_ru"),
                InlineKeyboardButton(text="Английский", callback_data="audio_lang_en")
            ],
            [
                InlineKeyboardButton(text="Авто-определение", callback_data="audio_lang_auto")
            ]
        ])
        
        await message.answer(
            "Аудио файл успешно загружен. Выберите язык для транскрибации:",
            reply_markup=markup
        )
        
        await state.set_state(States.waiting_audio_language)
    else:
        # Обрабатываем документы и изображения
        processing_result = await asyncio.to_thread(process_file, saved_path)
        
        if not processing_result["success"]:
            await message.answer(f"Ошибка при обработке файла: {processing_result['message']}")
            return
        
        # Сохраняем путь к файлу и его тип в состоянии
        await state.update_data(file_path=saved_path, file_type=processing_result["file_type"])
        
        # Если это изображение или документ, предлагаем проанализировать его
        if processing_result["file_type"] in ["image", "document", "text"]:
            await message.answer(
                "Файл успешно загружен. Что вы хотите узнать о нем? "
                "Введите вопрос или нажмите на одну из кнопок:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Общий анализ", callback_data="analyze_general")],
                    [InlineKeyboardButton(text="Выделить ключевые моменты", callback_data="analyze_key_points")],
                    [InlineKeyboardButton(text="Создать резюме", callback_data="analyze_summary")]
                ])
            )
            await state.set_state(States.waiting_document_question)
        else:
            await message.answer(
                f"Файл типа '{processing_result['file_type']}' успешно загружен, но его автоматическая обработка не поддерживается."
            )

# Обработчик выбора языка для транскрибации аудио
@router.callback_query(lambda c: c.data.startswith("audio_lang_"))
async def process_audio_language(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора языка для транскрибации аудио"""
    # Получаем данные из состояния
    data = await state.get_data()
    audio_file_path = data.get("audio_file_path")
    
    if not audio_file_path:
        await callback_query.message.answer("Не удалось получить информацию о файле.")
        await callback_query.answer()
        return
    
    # Определяем выбранный язык
    lang_code = callback_query.data.split("_")[2]
    language = None
    
    if lang_code != "auto":
        language = lang_code
    
    # Отправляем сообщение о начале транскрибации
    await callback_query.message.answer("🎤 Транскрибирую аудио файл...\nЭто может занять некоторое время.")
    
    # Выполняем транскрибацию
    transcription = await asyncio.to_thread(transcribe_audio, audio_file_path, language)
    
    # Отправляем результат транскрибации
    await callback_query.message.answer(f"📝 Транскрипция аудио:\n\n{transcription}")
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)
    
    # Отвечаем на колбэк
    await callback_query.answer()

# Обработчик инлайн кнопок для анализа документа
@router.callback_query(lambda c: c.data.startswith("analyze_"))
async def process_document_analysis(callback_query: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопки анализа документа"""
    # Получаем данные из состояния
    data = await state.get_data()
    file_path = data.get("file_path")
    file_type = data.get("file_type")
    
    if not file_path or not file_type:
        await callback_query.message.answer("Не удалось получить информацию о файле.")
        await callback_query.answer()
        return
    
    # Определяем тип анализа
    analysis_type = callback_query.data.split("_")[1]
    question = None
    
    if analysis_type == "general":
        question = "Проведите общий анализ содержимого."
    elif analysis_type == "key_points":
        question = "Выделите ключевые моменты и основные идеи."
    elif analysis_type == "summary":
        question = "Создайте краткое резюме содержимого."
    
    # Отправляем сообщение о начале анализа
    await callback_query.message.answer(f"🔍 Анализирую файл...\nЭто может занять некоторое время.")
    
    # Выполняем анализ
    result = await asyncio.to_thread(analyze_file_with_ai, file_path, question)
    
    # Отправляем результат
    await callback_query.message.answer(result)
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)
    
    # Отвечаем на колбэк
    await callback_query.answer()

# Обработчик вопроса о документе
@router.message(States.waiting_document_question)
async def process_document_question(message: Message, state: FSMContext):
    """Обработка вопроса о документе"""
    # Получаем данные из состояния
    data = await state.get_data()
    file_path = data.get("file_path")
    file_type = data.get("file_type")
    
    if not file_path or not file_type:
        await message.answer("Не удалось получить информацию о файле.")
        await state.set_state(States.main)
        return
    
    # Отправляем сообщение о начале анализа
    await message.answer(f"🔍 Анализирую файл для ответа на ваш вопрос...\nЭто может занять некоторое время.")
    
    # Выполняем анализ
    result = await asyncio.to_thread(analyze_file_with_ai, file_path, message.text)
    
    # Отправляем результат
    await message.answer(result)
    
    # Возвращаемся в основное состояние
    await state.set_state(States.main)

# Обработчик обычных текстовых сообщений
@router.message()
async def process_message(message: Message):
    """Обработка обычных текстовых сообщений"""
    # Получаем пользователя
    user = get_or_create_user(telegram_id=message.from_user.id)
    
    # Проверяем активный диалог или создаем новый
    conversation = get_active_conversation(user.id)
    if not conversation:
        conversation_id = create_conversation(user.id)
    else:
        conversation_id = conversation.id
    
    # Сохраняем сообщение пользователя
    add_message(conversation_id, "user", message.text)
    
    # Получаем ответ от ИИ
    system_prompt = "Вы помощник маркетолога. Отвечайте на вопросы пользователя, помогайте с маркетинговыми стратегиями, планированием и анализом. Всегда старайтесь давать конкретные и полезные советы. Отвечайте на русском языке."
    response = await asyncio.to_thread(get_text_response, message.text, system_prompt)
    
    # Сохраняем ответ бота
    add_message(conversation_id, "bot", response)
    
    # Отправляем ответ
    await message.answer(response)

# Функция для запуска бота
async def main():
    """Основная функция для запуска бота"""
    # Инициализируем бота
    await bot_startup()
    
    # Регистрируем роутер
    dp.include_router(router)
    
    # Запускаем бота
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main()) 