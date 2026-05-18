from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from auth.cookie import set_cookie, clear_session_cookie
from auth.security import decode_access_token, get_current_user, get_current_admin_user
import httpx
from datetime import date, datetime
from httpx import AsyncClient, AsyncHTTPTransport, HTTPStatusError, RequestError
from api.schemas import SProfileCreate, SMetricsCreate
import logging
from typing import Any
logger = logging.getLogger(__name__)
# Пул соединений для переиспользования клиента
transport = AsyncHTTPTransport(retries=3)
client_auth = AsyncClient(
    base_url="http://app_service:8002",
    timeout=5.0,
    transport=transport
)

router = APIRouter(prefix="/app")
def serialize_datetime(obj: Any) -> Any:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj
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
@router.post("/profile_update", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: SProfileCreate, current_id: str = Depends(get_current_user)):
    try:
        profile_dict = profile.model_dump()
        profile_dict = {
            key: serialize_datetime(value) for key, value in profile_dict.items()
        }
        auth_client = await client_auth.post(
            "/app/create_profile",
            json=profile_dict,
            headers={"X-User-Id": f"{current_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_profile", status_code=status.HTTP_200_OK)
async def get_profile(x_user_id: str = Depends(get_current_user)):
    try:
        auth_client = await client_auth.get(
            f"/app/get_profile",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---------------МЕТРИКА--------------
@router.post("/create_metrics", status_code=status.HTTP_201_CREATED)
async def create_metrics(metrics: SMetricsCreate, x_user_id: str = Depends(get_current_user)):
    try:
        metrics_dict = metrics.model_dump()
        auth_client = await client_auth.post(
            "/app/metrics/add_met",
            json=metrics_dict,
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_metrics", status_code=status.HTTP_200_OK)
async def get_metrics(x_user_id: str = Depends(get_current_user)):
    try:
        auth_client = await client_auth.get(
            "/app/metrics/get_metrics",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/update_metrics", status_code=status.HTTP_200_OK)
async def update_metrics(metric_id: int, metrics: SMetricsCreate, x_user_id: str = Depends(get_current_user)):
    try:
        metrics_dict = metrics.model_dump()
        auth_client = await client_auth.patch(
            f"/app/metrics/update_metrics/{metric_id}",
            json=metrics_dict,
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_metrics", status_code=status.HTTP_200_OK)
async def delete_metrics(metric_id: int, x_user_id: str = Depends(get_current_user)):
    try:
        auth_client = await client_auth.delete(
            f"/app/metrics/delete_metrics/{metric_id}",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#---------------СТАТИСТИКА--------------

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(x_user_id: str = Depends(get_current_user)):
    try:
        auth_client = await client_auth.get(
            "/app/stats/get_stats",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/detail", status_code=status.HTTP_200_OK)
async def get_stats_detail(x_user_id: str = Depends(get_current_user), days: int = 30):
    """Детальная статистика с данными для графиков"""
    try:
        auth_client = await client_auth.get(
            f"/app/stats/get_stats_detail?days={days}",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/metric/{metric_type}", status_code=status.HTTP_200_OK)
async def get_metric_detail(metric_type: str, x_user_id: str = Depends(get_current_user), days: int = 30):
    """Статистика по конкретной метрике"""
    try:
        auth_client = await client_auth.get(
            f"/app/stats/get_metric_detail/{metric_type}?days={days}",
            headers={"X-User-Id": f"{x_user_id}"}
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        return data
    except HTTPException as e:
        raise e
    except RequestError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))