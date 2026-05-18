from sqlalchemy import select, func
from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from database.models import Daily_metric
from database.method import connection
from datetime import timedelta, timezone, datetime
from api.logging_config import logger


@connection
async def get_steps_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по шагам."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.steps).label('total_steps'),
            func.avg(Daily_metric.steps).label('avg_steps'),
            func.min(Daily_metric.steps).label('min_steps'),
            func.max(Daily_metric.steps).label('max_steps')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    return {
        "metric": "steps",
        "display_name": "Шаги",
        "unit": "шагов",
        "total_days": row.total_days or 0,
        "total": float(row.total_steps or 0),
        "average": round(float(row.avg_steps or 0), 2),
        "min": row.min_steps or 0,
        "max": row.max_steps or 0
    }


@connection
async def get_calories_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по калориям (расход)."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.calories).label('total_calories'),
            func.avg(Daily_metric.calories).label('avg_calories'),
            func.min(Daily_metric.calories).label('min_calories'),
            func.max(Daily_metric.calories).label('max_calories')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    return {
        "metric": "calories",
        "display_name": "Калории (расход)",
        "unit": "ккал",
        "total_days": row.total_days or 0,
        "total": float(row.total_calories or 0),
        "average": round(float(row.avg_calories or 0), 2),
        "min": row.min_calories or 0,
        "max": row.max_calories or 0
    }


@connection
async def get_calories_intake_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по потреблённым калориям."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.calories_intake).label('total_intake'),
            func.avg(Daily_metric.calories_intake).label('avg_intake'),
            func.min(Daily_metric.calories_intake).label('min_intake'),
            func.max(Daily_metric.calories_intake).label('max_intake')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    return {
        "metric": "calories_intake",
        "display_name": "Калории (потребление)",
        "unit": "ккал",
        "total_days": row.total_days or 0,
        "total": float(row.total_intake or 0),
        "average": round(float(row.avg_intake or 0), 2),
        "min": row.min_intake or 0,
        "max": row.max_intake or 0
    }


@connection
async def get_sleep_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по сну."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.sleep_hours).label('total_sleep'),
            func.avg(Daily_metric.sleep_hours).label('avg_sleep'),
            func.min(Daily_metric.sleep_hours).label('min_sleep'),
            func.max(Daily_metric.sleep_hours).label('max_sleep'),
            func.avg(Daily_metric.sleep_score).label('avg_score')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    avg_score = row.avg_score or 0
    quality = "good" if avg_score >= 4 else "moderate" if avg_score >= 3 else "poor"
    return {
        "metric": "sleep",
        "display_name": "Сон",
        "unit": "часов",
        "total_days": row.total_days or 0,
        "total_hours": float(row.total_sleep or 0),
        "average_hours": round(float(row.avg_sleep or 0), 2),
        "min_hours": row.min_sleep or 0,
        "max_hours": row.max_sleep or 0,
        "average_score": round(float(avg_score), 2),
        "quality": quality
    }


@connection
async def get_water_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по воде."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.water_ml).label('total_water'),
            func.avg(Daily_metric.water_ml).label('avg_water'),
            func.min(Daily_metric.water_ml).label('min_water'),
            func.max(Daily_metric.water_ml).label('max_water')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    total = row.total_water or 0
    avg = row.avg_water or 0
    return {
        "metric": "water_ml",
        "display_name": "Вода",
        "unit": "мл",
        "total_days": row.total_days or 0,
        "total": float(total),
        "total_liters": round(float(total) / 1000, 2),
        "average": round(float(avg), 2),
        "average_liters": round(float(avg) / 1000, 2),
        "min": row.min_water or 0,
        "max": row.max_water or 0
    }


@connection
async def get_mood_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по настроению."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.avg(Daily_metric.mood).label('avg_mood'),
            func.min(Daily_metric.mood).label('min_mood'),
            func.max(Daily_metric.mood).label('max_mood')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    avg = row.avg_mood or 0
    assessment = "excellent" if avg >= 4 else "good" if avg >= 3 else "moderate" if avg >= 2 else "poor"
    return {
        "metric": "mood",
        "display_name": "Настроение",
        "unit": "баллов",
        "total_days": row.total_days or 0,
        "average": round(float(avg), 2),
        "min": row.min_mood or 0,
        "max": row.max_mood or 0,
        "assessment": assessment
    }


@connection
async def get_stress_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по стрессу."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.avg(Daily_metric.stress_level).label('avg_stress'),
            func.min(Daily_metric.stress_level).label('min_stress'),
            func.max(Daily_metric.stress_level).label('max_stress')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    avg = row.avg_stress or 0
    assessment = "low" if avg < 3 else "moderate" if avg < 4 else "high"
    return {
        "metric": "stress_level",
        "display_name": "Стресс",
        "unit": "баллов",
        "total_days": row.total_days or 0,
        "average": round(float(avg), 2),
        "min": row.min_stress or 0,
        "max": row.max_stress or 0,
        "assessment": assessment
    }


@connection
async def get_distance_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Статистика по дистанции."""
    session = kwargs.get('session')
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(
            func.count(Daily_metric.id).label('total_days'),
            func.sum(Daily_metric.distance).label('total_distance'),
            func.avg(Daily_metric.distance).label('avg_distance'),
            func.min(Daily_metric.distance).label('min_distance'),
            func.max(Daily_metric.distance).label('max_distance')
        ).where(
            Daily_metric.user_id == x_user_id,
            Daily_metric.date >= cutoff_date
        )
    )
    row = result.one()
    total = row.total_distance or 0
    avg = row.avg_distance or 0
    return {
        "metric": "distance",
        "display_name": "Дистанция",
        "unit": "км",
        "total_days": row.total_days or 0,
        "total": float(total),
        "total_meters": round(float(total) * 1000, 2),
        "average": round(float(avg), 2),
        "average_meters": round(float(avg) * 1000, 2),
        "min": row.min_distance or 0,
        "max": row.max_distance or 0
    }


@connection
async def get_all_metrics_stats(x_user_id: str, days: int = 10, **kwargs) -> Dict[str, Any]:
    """Полная статистика по всем метрикам."""
    return {
        "period_days": days,
        "steps": await get_steps_stats(x_user_id, days),
        "calories": await get_calories_stats(x_user_id, days),
        "calories_intake": await get_calories_intake_stats(x_user_id, days),
        "sleep": await get_sleep_stats(x_user_id, days),
        "water_ml": await get_water_stats(x_user_id, days),
        "mood": await get_mood_stats(x_user_id, days),
        "stress_level": await get_stress_stats(x_user_id, days),
        "distance": await get_distance_stats(x_user_id, days)
    }