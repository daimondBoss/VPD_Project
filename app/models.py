import uuid
import enum
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Numeric, ForeignKey, Enum, JSON, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# --- ENUM'ы для статусов ---
class TopicStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class PlanStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class SessionStatus(str, enum.Enum):
    PLANNED = "planned"
    DONE = "done"
    SKIPPED = "skipped"

# --- 1. Пользователи ---
class User(Base):
    __tablename__ = "users"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Изменили название для точности
    name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    settings = relationship("Settings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    exceptions = relationship("Exception", back_populates="user", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="user", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="user", cascade="all, delete-orphan")

# --- 2. Настройки пользователя ---
class Settings(Base):
    __tablename__ = "settings"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), unique=True, nullable=False)
    hours_per_day = Column(Numeric(3, 1), nullable=False)
    study_days_of_week = Column(JSON, nullable=False) # Аналог jsonb
    buffer_days_before_exam = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", back_populates="settings")

# --- 3. Исключения (Выходные/праздники) ---
class Exception(Base):
    __tablename__ = "exceptions"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)

    user = relationship("User", back_populates="exceptions")

# --- 4. Предметы ---
class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False) # Валидация длины будет в Pydantic
    color = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")

# --- 5. Темы ---
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    subject_id = Column(Uuid, ForeignKey("subjects.id"), nullable=False)
    title = Column(String, nullable=False)
    estimated_hours = Column(Numeric(4, 1), nullable=False)
    status = Column(Enum(TopicStatus), default=TopicStatus.TODO, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="topics")
    study_sessions = relationship("StudySession", back_populates="topic")

# --- 6. Экзамены ---
class Exam(Base):
    __tablename__ = "exams"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    subject_id = Column(Uuid, ForeignKey("subjects.id"), nullable=False)
    exam_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subject = relationship("Subject", back_populates="exams")

# --- 7. Планы подготовки ---
class StudyPlan(Base):
    __tablename__ = "study_plans"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    archived_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="study_plans")
    study_sessions = relationship("StudySession", back_populates="plan", cascade="all, delete-orphan")

# --- 8. Сессии обучения (ScheduleItem из вашего ТЗ) ---
class StudySession(Base):
    __tablename__ = "study_sessions"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    plan_id = Column(Uuid, ForeignKey("study_plans.id"), nullable=False)
    topic_id = Column(Uuid, ForeignKey("topics.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    planned_hours = Column(Numeric(3, 1), nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.PLANNED, nullable=False)
    is_manually_adjusted = Column(Boolean, default=False, nullable=False)
    done_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("StudyPlan", back_populates="study_sessions")
    topic = relationship("Topic", back_populates="study_sessions")