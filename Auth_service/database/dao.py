from sqlalchemy import select, delete, update
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from database.models import User
from database.method import connection
from datetime import timedelta
from datetime import datetime
from random import randint
import random
from sqlalchemy.exc import IntegrityError
from api.logging_config import logger
@connection
async def add_user(session, email, password, first_name, last_name, phone_number):
    logger.info(f"add_user: Начало для email: {email}")
    
    try:
        logger.info(f"add_user: Проверка существующего пользователя для {email}")
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        existing_user = result.scalar()
        
        if existing_user:
            logger.warning(f"add_user: Пользователь с email {email} уже существует в сессии БД")
            return None
        
        logger.info(f"add_user: Создаём нового пользователя для {email}")
        new_user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        
        session.add(new_user)
        logger.info(f"add_user: Пользователь добавлен в сессию, делаем commit")
        
        await session.commit()
        logger.info(f"add_user: Commit выполнен успешно")
        
        await session.refresh(new_user)
        logger.info(f"add_user: Refresh выполнен, user_id: {new_user.user_id}")
        
        result_dict = {
            "user_id": new_user.user_id,
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "phone_number": new_user.phone_number,
        }
        
        logger.info(f"add_user: УСПЕХ! Возвращаем: {result_dict}")
        return result_dict
    
    except IntegrityError as e:
        # Уникальность нарушена (email или другой unique field)
        await session.rollback()
        logger.error(f"add_user: IntegrityError для {email}: {type(e).__name__} - {e}")
        logger.error(f"add_user: Статус сессии после rollback: {session.is_active}")
        return None
    
    except SQLAlchemyError as e:
        # Другие ошибки SQLAlchemy
        await session.rollback()
        logger.error(f"add_user: SQLAlchemyError для {email}: {type(e).__name__} - {e}")
        logger.error(f"add_user: Статус сессии после rollback: {session.is_active}")
        raise e
    
    except Exception as e:
        # Любые другие ошибки
        await session.rollback()
        logger.error(f"add_user: НЕИЗВЕСТНАЯ ОШИБКА для {email}: {type(e).__name__} - {e}", exc_info=True)
        logger.error(f"add_user: Статус сессии после rollback: {session.is_active}")
        raise e
@connection
async def get_user_by_email(session, email):
    try:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar()
        if user is None:
            return None
        return {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "password": user.password
        }
    except SQLAlchemyError as e:
        raise e

@connection
async def delete_user_dao(session, user_id):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        if user is None:
            return None
        await session.delete(user)
        await session.commit()
        return {"message": "Пользователь успешно удален"}
    except SQLAlchemyError as e:
        await session.rollback()
        raise e

@connection
async def get_user_by_id(session, user_id):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        if user is None:
            return None
        return {
            "user_id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
        }
    except SQLAlchemyError as e:
        raise e

@connection
async def update_user_dao(session, user_id, **kwargs):
    try:
        query = update(User).where(User.user_id == user_id).values(**kwargs)
        await session.execute(query)
        await session.commit()
        return {"message": "Пользователь успешно обновлен"}
    except SQLAlchemyError as e:
        await session.rollback()
        raise e

@connection
async def is_admin_user(session, user_id: str) -> bool|str:
    try:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar()
        if user is None:
            return None
        return user.is_admin
    except SQLAlchemyError as e:
        raise e