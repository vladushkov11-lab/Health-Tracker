from sqlalchemy import ForeignKey, String, ARRAY, text, Text, JSON, BigInteger, Integer, Boolean, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from database.enum import Gender, Workout_type
from datetime import datetime
from database.base import Base
from sqlalchemy import ForeignKey
from enum import Enum

class User(Base):
    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    birth_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    height: Mapped[int] = mapped_column(Integer, default=0) # Рост в см
    weight: Mapped[int] = mapped_column(Integer, default=0) # Вес в кг
    gender: Mapped[Gender] = mapped_column(String, default="") # Пол
    target_weight: Mapped[int] = mapped_column(Integer, default=0) # Целевой вес
    daily_step_goal: Mapped[int] = mapped_column(Integer, default=0) # Цельные шаги в день
    
    daily_metric = relationship("Daily_metric", back_populates="user", cascade="all, delete-orphan")
    workout_session = relationship("Workout_session", back_populates="user", cascade="all, delete-orphan")

class Daily_metric(Base): # Метрики за день
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, index=True)
    steps: Mapped[int] = mapped_column(Integer) # Шаги
    calories: Mapped[int] = mapped_column(Integer) # Калории
    distance: Mapped[float] = mapped_column(Numeric(10, 2)) # Дистанция
    sleep_hours: Mapped[int] = mapped_column(Integer) # Сон(колличество)
    sleep_score: Mapped[int] = mapped_column(Integer) # Сон(качество от 1 до 5)
    calories_intake: Mapped[int] = mapped_column(Integer) # Калории потреблённые
    water_ml: Mapped[int] = mapped_column(Integer) # Вода в мл
    mood: Mapped[int] = mapped_column(Integer) # Настроение от 1 до 5
    stress_level: Mapped[int] = mapped_column(Integer) # Стресс от 1 до 5
    
    user = relationship("User", back_populates="daily_metric")

class Workout_session(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    workout_type: Mapped[Workout_type] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    duration: Mapped[int] = mapped_column(Integer) # Длительность в минутах
    calories: Mapped[int] = mapped_column(Integer) # Калории
    distance: Mapped[float] = mapped_column(Numeric(10, 2)) # Дистанция
    notes: Mapped[str] = mapped_column(Text) # Заметки пользователя
    
    user = relationship("User", back_populates="workout_session")