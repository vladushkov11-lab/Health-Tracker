from sqlalchemy import select, delete, update
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from database.models import User
from database.method import connection
from datetime import timedelta
from datetime import datetime
from random import randint
import random
from api.logging_config import logger
@connection
async def get_user_by_id(session, user_id):
    try:
        logger.info(f"=== GET USER START ===")
        logger.info(f"Looking for user_id type: {type(user_id)}, value: '{user_id}'")  # ✅
        logger.info(f"Length: {len(user_id)}")  # ✅
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one()
        if user is None:
            logger.info(f"Query result: {user is not None}")
            return None
        logger.info(f"Found user_id: '{user.user_id}'")  # ✅
        logger.info(f"Match: {user.user_id == user_id}")
        return user
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user: {e}")


@connection
async def add_user(session, user_id, email, first_name, last_name):
    if await get_user_by_id(user_id=user_id) is not None:
        logger.warning(f"User with id {user_id} already exists")
        return None
    try:
        new_user = User(user_id=user_id, email=email, first_name=first_name, last_name=last_name)
        session.add(new_user)
        await session.commit()
        logger.info(f"User {user_id} added successfully")
        return new_user
    except SQLAlchemyError as e:
        logger.error(f"Error adding user: {e}")
        await session.rollback()
        raise e

@connection
async def add_profile(session, birth_date: datetime, height: int, weight: int, gender: str, target_weight: int, daily_step_goal: int, user_id: str):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            if birth_date is not None:
                user.birth_date = birth_date
            if height is not None:
                user.height = height
            if weight is not None:
                user.weight = weight
            if gender is not None:
                user.gender = gender
            if target_weight is not None:
                user.target_weight = target_weight
            if daily_step_goal is not None:
                user.daily_step_goal = daily_step_goal
            await session.commit()
            logger.info(f"Профиль пользователя {user_id} обновлен")
            return {
                "user_id": user.user_id,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "height": user.height,
                "weight": user.weight,
                "gender": user.gender,
                "target_weight": user.target_weight,
                "daily_step_goal": user.daily_step_goal
            }
        else:
            logger.warning(f"Пользователь с id {user_id} не найден")
            return None
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении профиля пользователя: {e}")
        await session.rollback()
        return None

@connection
async def get_profile_by_id(session, user_id):
    try:
        profile = await get_user_by_id(user_id=user_id)
        if profile is None:
            return None
        return {
            "user_id": profile.user_id,
            "birth_date": profile.birth_date.isoformat() if profile.birth_date else None,
            "height": profile.height,
            "weight": profile.weight,
            "gender": profile.gender,
            "target_weight": profile.target_weight,
            "daily_step_goal": profile.daily_step_goal
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении профиля пользователя: {e}")
        return None

@connection
async def delete_user(session, user_id):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if user:
            await session.delete(user)
            await session.commit()
            logger.info(f"Пользователь с id {user_id} удалён")
            return {"message": "Пользователь успешно удалён", "status": "ok"}
        else:
            logger.warning(f"Пользователь с id {user_id} не найден")
            return {"message": "Пользователь не найден", "status": "error"}
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        await session.rollback()
        return {"message": f"Ошибка при удалении пользователя: {e}", "status": "error"}