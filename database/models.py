from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# Создание базового класса для моделей
Base = declarative_base()

# URL для подключения к базе данных
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Пользователи
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_admin = Column(Boolean, default=False)
    
    # Связи с другими таблицами
    projects = relationship("Project", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"

# Проекты
class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="активен")  # активен, приостановлен, завершен и т.д.
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    completion_percentage = Column(Float, default=0.0)
    metadata = Column(JSON, nullable=True)
    
    # Связи с другими таблицами
    user = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    documents = relationship("Document", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.name}>"
    
    def set_metadata(self, data):
        self.metadata = json.dumps(data)
    
    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}

# Задачи проекта
class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="новая")  # новая, в работе, завершена и т.д.
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)  # 1-низкий, 2-средний, 3-высокий
    
    # Связи с другими таблицами
    project = relationship("Project", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task {self.name}>"

# Документы
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(50), nullable=True)  # текст, изображение, аудио и т.д.
    content_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    file_size = Column(Integer, nullable=True)  # размер в байтах
    
    # Связи с другими таблицами
    project = relationship("Project", back_populates="documents")
    
    def __repr__(self):
        return f"<Document {self.name}>"

# Диалоги с ботом
class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Связи с другими таблицами
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    
    def __repr__(self):
        return f"<Conversation {self.id}>"

# Сообщения в диалоге
class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    sender_type = Column(String(20), nullable=False)  # user, bot
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    metadata = Column(JSON, nullable=True)  # для хранения дополнительных данных
    
    # Связи с другими таблицами
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id}>"
    
    def set_metadata(self, data):
        self.metadata = json.dumps(data)
    
    def get_metadata(self):
        return json.loads(self.metadata) if self.metadata else {}

# Функция для инициализации базы данных
def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

# Если скрипт запущен напрямую, создаем все таблицы
if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("База данных успешно инициализирована.") 