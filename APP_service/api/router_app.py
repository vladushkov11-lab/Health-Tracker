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
router = APIRouter(prefix="/app/metrics", tags=["Metrics"])
def deserialize_datetime(value: Any) -> datetime | None:
    """Преобразует строку в datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return None
    return None
def serialize_datetime(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj
@router.post("/add_met", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_metrics(user_data: SMetricsCreate, x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        user_data_dict = user_data.model_dump()
        new_metrics = await add_metrics(x_user_id=x_user_id,
                                        data_of_metrics=user_data_dict["date_of_metrics"],
                                        steps=user_data_dict["steps"],
                                        calories=user_data_dict["calories"],
                                        distance=user_data_dict["distance"],
                                        sleep_hours=user_data_dict["sleep_hours"],
                                        sleep_score=user_data_dict["sleep_score"],
                                        calories_intake=user_data_dict["calories_intake"],
                                        water_ml=user_data_dict["water_ml"],
                                        mood=user_data_dict["mood"],
                                        stress_level=user_data_dict["stress_level"]
                                        )
        return {"message": "Metrics added successfully", "metrics": new_metrics}
    except Exception as e:
        logger.error(f"Error adding metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to add metrics")
    

@router.get("/get_metrics", response_model=list[dict], status_code=status.HTTP_200_OK)
async def get_all_metrics(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        metrics = await get_metrics_by_user_id(x_user_id=x_user_id)
        if not metrics:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metrics not found")
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to fetch metrics")
    
@router.patch("/update_metrics/{metric_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def upd_metrics(metric_id: int, user_data: SMetricsCreate, x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        user_data_dict = user_data.model_dump()
        updated_metrics = await update_metrics(metric_id=metric_id,
                                                x_user_id=x_user_id,
                                                steps=user_data_dict["steps"],
                                                calories=user_data_dict["calories"],
                                                distance=user_data_dict["distance"],
                                                sleep_hours=user_data_dict["sleep_hours"],
                                                sleep_score=user_data_dict["sleep_score"],
                                                calories_intake=user_data_dict["calories_intake"],
                                                water_ml=user_data_dict["water_ml"],
                                                mood=user_data_dict["mood"],
                                                stress_level=user_data_dict["stress_level"]
                                                )
        return {"message": "Metrics updated successfully", "metrics": updated_metrics}
    except Exception as e:
        logger.error(f"Error updating metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to update metrics")
    
@router.delete("/delete_metrics/{metric_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_m(metric_id: int, x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        deleted_metrics = await delete_metrics(metric_id=metric_id, x_user_id=x_user_id)
        return {"message": "Metrics deleted successfully", "metrics": deleted_metrics}
    except Exception as e:
        logger.error(f"Error deleting metrics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Failed to delete metrics")
        