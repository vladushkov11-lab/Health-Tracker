from sqlalchemy import select, delete, update
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from database.models import User, Daily_metric
from database.method import connection
from datetime import timedelta, timezone, datetime
from api.logging_config import logger

METRIC_TTL_DAYS = 10


def get_cutoff_date() -> datetime:
    """Возвращает дату отсечения для метрик (сегодня - 10 дней)."""
    return datetime.now(timezone.utc) - timedelta(days=METRIC_TTL_DAYS)

async def cleanup_old_metrics(session, user_id: str = None) -> int:
    
    try:
        cutoff_date = get_cutoff_date()
        
        # 1. Сначала находим ID старых метрик
        query = select(Daily_metric.id).where(
            Daily_metric.date < cutoff_date
        )
        if user_id is not None:
            query = query.where(Daily_metric.user_id == user_id)
        
        result = await session.execute(query)
        metric_ids = [row[0] for row in result.all()]
        
        if not metric_ids:
            logger.debug(f"No old metrics to delete for user_id={user_id}")
            return 0
        
        # 2. Удаляем найденные метрики
        delete_query = delete(Daily_metric).where(Daily_metric.id.in_(metric_ids))
        delete_result = await session.execute(delete_query)
        deleted_count = delete_result.rowcount
        
        # 3. Коммитим изменения
        await session.commit()
        
        logger.info(f"Deleted {deleted_count} old metrics for user_id={user_id}")
        return deleted_count
    
    except SQLAlchemyError as e:
        logger.error(f"Error cleaning up old metrics: {e}")
        await session.rollback()
        raise e


@connection
async def add_metrics(session, data_of_metrics, x_user_id: str, 
                        steps: int|None = None, 
                        calories: int|None = None, 
                        distance: float|None = None, 
                        sleep_hours: int|None = None, 
                        sleep_score: int|None = None, 
                        calories_intake: int|None = None, 
                        water_ml: int|None = None, 
                        mood: int|None = None, 
                        stress_level: int|None = None):
    try:
        if isinstance(data_of_metrics, str):
            data_of_metrics = datetime.fromisoformat(data_of_metrics.replace('Z', '+00:00'))
        new_metrics = Daily_metric(
            user_id=x_user_id,
            date=data_of_metrics,
            steps=steps,
            calories=calories,
            distance=distance,
            sleep_hours=sleep_hours,
            sleep_score=sleep_score,
            calories_intake=calories_intake,
            water_ml=water_ml,
            mood=mood,
            stress_level=stress_level
        )
        session.add(new_metrics)
        await session.commit()
        await session.refresh(new_metrics)
        logger.info(f"Metrics added successfully for user {x_user_id}")
        return {
            "user_id": new_metrics.user_id,
            "data": new_metrics.date,
            "steps": new_metrics.steps,
            "calories": new_metrics.calories,
            "distance": new_metrics.distance,
            "sleep_hours": new_metrics.sleep_hours,
            "sleep_score": new_metrics.sleep_score,
            "calories_intake": new_metrics.calories_intake,
            "water_ml": new_metrics.water_ml,
            "mood": new_metrics.mood,
            "stress_level": new_metrics.stress_level
        }
    except SQLAlchemyError as e:
        logger.error(f"Error adding metrics: {e}")
        await session.rollback()
        raise e


@connection
async def get_metrics_by_id(session, metric_id: int) -> Optional[Dict[str, Any]]:
    try:
        result = await session.execute(
            select(Daily_metric).where(Daily_metric.id == metric_id)
        )
        metric = result.scalar_one_or_none()
        if metric:
            return {
                "id": metric.id,
                "user_id": metric.user_id,
                "date": metric.date,
                "steps": metric.steps,
                "calories": metric.calories,
                "distance": metric.distance,
                "sleep_hours": metric.sleep_hours,
                "sleep_score": metric.sleep_score,
                "calories_intake": metric.calories_intake,
                "water_ml": metric.water_ml,
                "mood": metric.mood,
                "stress_level": metric.stress_level
            }
        return None
    except SQLAlchemyError as e:
        logger.error(f"Error getting metric by id: {e}")
        raise e


@connection
async def update_metrics(session, metric_id: int, x_user_id: str, 
                            steps: Optional[int] = None, 
                            calories: Optional[int] = None, 
                            distance: Optional[float] = None, 
                            sleep_hours: Optional[int] = None, 
                            sleep_score: Optional[int] = None, 
                            calories_intake: Optional[int] = None, 
                            water_ml: Optional[int] = None, 
                            mood: Optional[int] = None, 
                            stress_level: Optional[int] = None) -> Dict[str, Any]:
    try:
        result = await session.execute(
            select(Daily_metric).where(
                Daily_metric.id == metric_id,
                Daily_metric.user_id == x_user_id
            )
        )
        metric = result.scalar_one_or_none()
        if not metric:
            logger.error(f"Metric not found: {metric_id}")
            return {"error": "Metric not found"}
        
        if steps is not None:
            metric.steps = steps
        if calories is not None:
            metric.calories = calories
        if distance is not None:
            metric.distance = distance
        if sleep_hours is not None:
            metric.sleep_hours = sleep_hours
        if sleep_score is not None:
            metric.sleep_score = sleep_score
        if calories_intake is not None:
            metric.calories_intake = calories_intake
        if water_ml is not None:
            metric.water_ml = water_ml
        if mood is not None:
            metric.mood = mood
        if stress_level is not None:
            metric.stress_level = stress_level
        
        await session.commit()
        await session.refresh(metric)
        logger.info(f"Metrics updated successfully for metric {metric_id}")
        return {
            "id": metric.id,
            "user_id": metric.user_id,
            "date": metric.date,
            "steps": metric.steps,
            "calories": metric.calories,
            "distance": metric.distance,
            "sleep_hours": metric.sleep_hours,
            "sleep_score": metric.sleep_score,
            "calories_intake": metric.calories_intake,
            "water_ml": metric.water_ml,
            "mood": metric.mood,
            "stress_level": metric.stress_level
        }
    except SQLAlchemyError as e:
        logger.error(f"Error updating metrics: {e}")
        await session.rollback()
        raise e


@connection
async def delete_metrics(session, metric_id: int, x_user_id: str) -> Dict[str, str]:
    try:
        result = await session.execute(
            select(Daily_metric).where(
                Daily_metric.id == metric_id,
                Daily_metric.user_id == x_user_id
            )
        )
        metric = result.scalar_one_or_none()
        if not metric:
            logger.error(f"Metric not found: {metric_id}")
            return {"error": "Metric not found"}
        
        await session.delete(metric)
        await session.commit()
        logger.info(f"Metrics deleted successfully: {metric_id}")
        return {"message": "Metrics deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Error deleting metrics: {e}")
        await session.rollback()
        raise e


@connection
async def get_metrics_by_user_id(session, x_user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Получает метрики пользователя за последние N дней."""
    # Очищаем старые метрики ПЕРЕД запросом (синхронная версия)
    try:
        delete_count = await cleanup_old_metrics(session, x_user_id)
        if delete_count > 0:
            logger.info(f"Deleted {delete_count} old metrics")
    except Exception as e:
        logger.warning(f"Could not cleanup old metrics: {e}")
    
    try:
        result = await session.execute(
            select(Daily_metric)
            .where(Daily_metric.user_id == x_user_id)
            .order_by(Daily_metric.date.desc())
            .limit(limit)
        )
        metrics = result.scalars().all()
        return [{
            "id": m.id,
            "user_id": m.user_id,
            "date_of_metrics": m.date,
            "steps": m.steps,
            "calories": m.calories,
            "distance": float(m.distance) if m.distance else 0,
            "sleep_hours": m.sleep_hours,
            "sleep_score": m.sleep_score,
            "calories_intake": m.calories_intake,
            "water_ml": m.water_ml,
            "mood": m.mood,
            "stress_level": m.stress_level
        } for m in metrics]
    except SQLAlchemyError as e:
        logger.error(f"Error getting metrics: {e}")
        raise e