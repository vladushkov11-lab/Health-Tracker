from sqlalchemy import ForeignKey, String, ARRAY, text, Text, JSON, BigInteger, Integer, Boolean, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from datetime import datetime
from database.base import Base
from sqlalchemy import ForeignKey
from enum import Enum
from database.utils import generate_id_user

class User(Base):
    user_id: Mapped[str] = mapped_column(String(32), default=generate_id_user, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)