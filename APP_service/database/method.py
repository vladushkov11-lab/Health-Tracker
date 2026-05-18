from datetime import datetime
from sqlalchemy import Integer, func, ARRAY, String, JSON
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from database.base import DATABASE_URL, Base
engine = create_async_engine(
    DATABASE_URL,
    )

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await session.close()  # Закрываем сессию

    return wrapper

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)