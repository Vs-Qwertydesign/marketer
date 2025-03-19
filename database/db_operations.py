from sqlalchemy import create_engine, select, update, desc
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from database.models import Base, User, Project, Task, Document, Conversation, Message

# Создаем строку подключения к базе данных
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Инициализирует базу данных, создавая все таблицы
    """
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """
    Возвращает сессию базы данных
    
    Returns:
        Объект сессии SQLAlchemy
    """
    session = SessionLocal()
    try:
        return session
    finally:
        session.close()

def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    """
    Возвращает существующего пользователя или создает нового
    
    Args:
        telegram_id: Telegram ID пользователя
        username: Имя пользователя в Telegram
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        
    Returns:
        Объект пользователя
    """
    session = get_db_session()
    
    # Ищем пользователя
    user = session.execute(
        select(User).where(User.telegram_id == telegram_id)
    ).scalar_one_or_none()
    
    # Если пользователь не найден, создаем нового
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    
    # Если пользователь существует, обновляем информацию
    elif username and (user.username != username or user.first_name != first_name or user.last_name != last_name):
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.updated_at = datetime.now()
        session.commit()
        session.refresh(user)
    
    return user

def get_all_users() -> List[User]:
    """
    Возвращает список всех пользователей
    
    Returns:
        Список объектов пользователей
    """
    session = get_db_session()
    users = session.execute(select(User)).scalars().all()
    return users

def create_project(user_id: int, name: str, description: str = None) -> int:
    """
    Создает новый проект
    
    Args:
        user_id: ID пользователя
        name: Название проекта
        description: Описание проекта
        
    Returns:
        ID созданного проекта
    """
    session = get_db_session()
    
    # Создаем проект
    project = Project(
        user_id=user_id,
        name=name,
        description=description,
        status="active"
    )
    
    session.add(project)
    session.commit()
    session.refresh(project)
    
    return project.id

def get_projects_by_user(user_id: int) -> List[Project]:
    """
    Возвращает список проектов пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список проектов пользователя
    """
    session = get_db_session()
    
    projects = session.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(desc(Project.created_at))
    ).scalars().all()
    
    return projects

def get_project_by_id(project_id: int) -> Optional[Project]:
    """
    Возвращает проект по ID
    
    Args:
        project_id: ID проекта
        
    Returns:
        Объект проекта или None, если проект не найден
    """
    session = get_db_session()
    
    project = session.execute(
        select(Project)
        .where(Project.id == project_id)
    ).scalar_one_or_none()
    
    return project

def update_project_status(project_id: int, status: str) -> bool:
    """
    Обновляет статус проекта
    
    Args:
        project_id: ID проекта
        status: Новый статус
        
    Returns:
        True, если статус обновлен, иначе False
    """
    session = get_db_session()
    
    # Проверяем, что проект существует
    project = session.execute(
        select(Project)
        .where(Project.id == project_id)
    ).scalar_one_or_none()
    
    if not project:
        return False
    
    # Обновляем статус
    session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(status=status, updated_at=datetime.now())
    )
    
    session.commit()
    
    return True

def create_task(project_id: int, title: str, description: str = None, due_date: datetime = None) -> int:
    """
    Создает новую задачу в проекте
    
    Args:
        project_id: ID проекта
        title: Название задачи
        description: Описание задачи
        due_date: Срок выполнения
        
    Returns:
        ID созданной задачи
    """
    session = get_db_session()
    
    # Создаем задачу
    task = Task(
        project_id=project_id,
        title=title,
        description=description,
        due_date=due_date,
        status="pending"
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)
    
    return task.id

def get_tasks_by_project(project_id: int) -> List[Task]:
    """
    Возвращает список задач проекта
    
    Args:
        project_id: ID проекта
        
    Returns:
        Список задач проекта
    """
    session = get_db_session()
    
    tasks = session.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .order_by(desc(Task.created_at))
    ).scalars().all()
    
    return tasks

def update_task_status(task_id: int, status: str) -> bool:
    """
    Обновляет статус задачи
    
    Args:
        task_id: ID задачи
        status: Новый статус
        
    Returns:
        True, если статус обновлен, иначе False
    """
    session = get_db_session()
    
    # Проверяем, что задача существует
    task = session.execute(
        select(Task)
        .where(Task.id == task_id)
    ).scalar_one_or_none()
    
    if not task:
        return False
    
    # Обновляем статус
    session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(status=status, updated_at=datetime.now())
    )
    
    session.commit()
    
    return True

def save_document(user_id: int, project_id: int, name: str, file_path: str, file_type: str) -> int:
    """
    Сохраняет документ
    
    Args:
        user_id: ID пользователя
        project_id: ID проекта
        name: Название документа
        file_path: Путь к файлу
        file_type: Тип файла
        
    Returns:
        ID сохраненного документа
    """
    session = get_db_session()
    
    # Создаем документ
    document = Document(
        user_id=user_id,
        project_id=project_id,
        name=name,
        file_path=file_path,
        file_type=file_type
    )
    
    session.add(document)
    session.commit()
    session.refresh(document)
    
    return document.id

def get_documents_by_project(project_id: int) -> List[Document]:
    """
    Возвращает список документов проекта
    
    Args:
        project_id: ID проекта
        
    Returns:
        Список документов проекта
    """
    session = get_db_session()
    
    documents = session.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(desc(Document.created_at))
    ).scalars().all()
    
    return documents

def create_conversation(user_id: int, project_id: int = None) -> int:
    """
    Создает новый диалог
    
    Args:
        user_id: ID пользователя
        project_id: ID проекта (опционально)
        
    Returns:
        ID созданного диалога
    """
    session = get_db_session()
    
    # Создаем диалог
    conversation = Conversation(
        user_id=user_id,
        project_id=project_id,
        status="active"
    )
    
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    
    return conversation.id

def get_active_conversation(user_id: int, project_id: int = None) -> Optional[Conversation]:
    """
    Возвращает активный диалог пользователя
    
    Args:
        user_id: ID пользователя
        project_id: ID проекта (опционально)
        
    Returns:
        Объект диалога или None, если диалог не найден
    """
    session = get_db_session()
    
    # Строим базовый запрос
    query = select(Conversation).where(
        (Conversation.user_id == user_id) & 
        (Conversation.status == "active")
    )
    
    # Если указан ID проекта, добавляем условие
    if project_id:
        query = query.where(Conversation.project_id == project_id)
    
    # Получаем последний активный диалог
    conversation = session.execute(
        query.order_by(desc(Conversation.created_at))
    ).scalar_one_or_none()
    
    return conversation

def add_message(conversation_id: int, role: str, content: str) -> int:
    """
    Добавляет сообщение в диалог
    
    Args:
        conversation_id: ID диалога
        role: Роль отправителя (user/bot)
        content: Содержимое сообщения
        
    Returns:
        ID добавленного сообщения
    """
    session = get_db_session()
    
    # Создаем сообщение
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    
    session.add(message)
    session.commit()
    session.refresh(message)
    
    return message.id

def get_conversation_messages(conversation_id: int) -> List[Message]:
    """
    Возвращает список сообщений диалога
    
    Args:
        conversation_id: ID диалога
        
    Returns:
        Список сообщений диалога
    """
    session = get_db_session()
    
    messages = session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    ).scalars().all()
    
    return messages 