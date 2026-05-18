from fastapi import APIRouter, HTTPException, status, Depends, Header
from database.dao_user import get_user_by_id, add_user, add_profile, get_profile_by_id, delete_user
from database.dao_app import (
    add_metrics,
    get_metrics_by_user_id,
    update_metrics,
    delete_metrics
)
from api.utils_stats import get_user_stats
from api.schemas import SMetricsCreate
import httpx
from datetime import datetime, date
from typing import Any
from api.logging_config import logger
router = APIRouter(prefix="/app/stats", tags=["Metrics"])

@router.get("/get_stats", response_model=dict, status_code=status.HTTP_200_OK)
async def get_stats(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        metrics = await get_metrics_by_user_id(x_user_id = x_user_id)
        user_data = await get_profile_by_id(user_id=x_user_id)
        stats = await get_user_stats(x_user_id=x_user_id, user_data=user_data)
        return stats
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch stats")
    
@router.get("/get_stats_detail", response_model=dict, status_code=status.HTTP_200_OK)
async def get_stats_detail(x_user_id: str = Header(default=None, alias="X-User-Id"), days: int = 30):
    """Получить детальную статистику по всем метрикам с данными для графиков"""
    try:
        metrics = await get_metrics_by_user_id(x_user_id=x_user_id)
        user_data = await get_profile_by_id(user_id=x_user_id)
        
        # Фильтруем метрики за последние days дней
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_metrics = []
        for m in metrics:
            try:
                metric_date = datetime.fromisoformat(m['date_of_metrics'])
                if metric_date >= cutoff_date:
                    filtered_metrics.append(m)
            except:
                filtered_metrics.append(m)
        
        # Сортируем по дате
        filtered_metrics.sort(key=lambda x: x.get('date_of_metrics', ''), reverse=True)
        
        # Формируем данные для графиков
        chart_data = {
            "labels": [],
            "datasets": {
                "steps": [],
                "calories": [],
                "distance": [],
                "sleep_hours": [],
                "mood": [],
                "stress_level": [],
                "water_ml": [],
                "calories_intake": []
            }
        }
        
        for metric in reversed(filtered_metrics):
            date_str = metric.get('date_of_metrics', '')[:10]
            chart_data["labels"].append(date_str)
            chart_data["datasets"]["steps"].append(metric.get('steps', 0))
            chart_data["datasets"]["calories"].append(metric.get('calories', 0))
            chart_data["datasets"]["distance"].append(metric.get('distance', 0))
            chart_data["datasets"]["sleep_hours"].append(metric.get('sleep_hours', 0))
            chart_data["datasets"]["mood"].append(metric.get('mood', 0))
            chart_data["datasets"]["stress_level"].append(metric.get('stress_level', 0))
            chart_data["datasets"]["water_ml"].append(metric.get('water_ml', 0))
            chart_data["datasets"]["calories_intake"].append(metric.get('calories_intake', 0))
        
        # Общая статистика
        stats = await get_user_stats(x_user_id=x_user_id, user_data=user_data, days=days)
        
        return {
            "total_metrics": len(filtered_metrics),
            "days": days,
            "chart_data": chart_data,
            "stats": stats,
            "metrics": filtered_metrics
        }
    except Exception as e:
        logger.error(f"Error fetching detailed stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch detailed stats")

@router.get("/get_metric_detail/{metric_type}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_metric_detail(metric_type: str, x_user_id: str = Header(default=None, alias="X-User-Id"), days: int = 30):
    """Получить детальную статистику по конкретной метрике"""
    try:
        metrics = await get_metrics_by_user_id(x_user_id=x_user_id)
        user_data = await get_profile_by_id(user_id=x_user_id)
        
        # Фильтруем метрики за последние days дней
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_metrics = []
        for m in metrics:
            try:
                metric_date = datetime.fromisoformat(m['date_of_metrics'])
                if metric_date >= cutoff_date:
                    filtered_metrics.append(m)
            except:
                filtered_metrics.append(m)
        
        # Сортируем по дате
        filtered_metrics.sort(key=lambda x: x.get('date_of_metrics', ''), reverse=True)
        
        # Формируем данные для графика конкретной метрики
        metric_field_map = {
            "steps": "steps",
            "calories": "calories",
            "distance": "distance",
            "sleep": "sleep_hours",
            "mood": "mood",
            "stress": "stress_level",
            "water": "water_ml",
            "calories_intake": "calories_intake"
        }
        
        field = metric_field_map.get(metric_type, metric_type)
        
        chart_data = {
            "labels": [],
            "values": [],
            "metric": field
        }
        
        # Расчёт статистики для конкретной метрики
        values = []
        for metric in reversed(filtered_metrics):
            date_str = metric.get('date_of_metrics', '')[:10]
            value = metric.get(field, 0)
            chart_data["labels"].append(date_str)
            chart_data["values"].append(value)
            values.append(value)
        
        # Статистика по метрике
        metric_stats = {
            "metric": metric_type,
            "count": len(values),
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "average": round(sum(values) / len(values), 2) if values else 0,
            "total": sum(values) if values else 0,
            "last_value": values[-1] if values else None,
            "trend": None
        }
        if len(values) >= 4:
            half = len(values) // 2
            first_half_avg = sum(values[:half]) / half
            second_half_avg = sum(values[half:]) / (len(values) - half)
            if second_half_avg > first_half_avg * 1.1:
                metric_stats["trend"] = "up"
            elif second_half_avg < first_half_avg * 0.9:
                metric_stats["trend"] = "down"
            else:
                metric_stats["trend"] = "stable"
        
        return {
            "total_metrics": len(filtered_metrics),
            "days": days,
            "chart_data": chart_data,
            "metric_stats": metric_stats
        }
    except Exception as e:
        logger.error(f"Error fetching metric detail: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch metric detail")