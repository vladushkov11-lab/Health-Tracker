from fastapi import APIRouter, HTTPException, status, Depends, Header
from database.dao_user import get_user_by_id, add_user, add_profile, get_profile_by_id, delete_user
from api.schemas import SUserCreate, SProfileCreate

import httpx
from datetime import datetime, date
from typing import Any
from api.logging_config import logger

router = APIRouter(prefix="/app")
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
@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(user: SUserCreate):
    try:
        user_dict = user.model_dump()
        user = await add_user(
            user_id=user_dict["user_id"],
            email=user_dict["email"],
            first_name=user_dict["first_name"],
            last_name=user_dict["last_name"],
        )
        if user is None:
            user_id = user_dict["user_id"]
            return {"message": f"Пользователь с таким {user_id} уже существует", "status": "error"}
        return {"message": "Пользователь успешно создан", "status": "ok"}
    except HTTPException as e:
        raise e

@router.post("/create_profile", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: SProfileCreate, x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан user_id"
            )
        profile_dict = profile.model_dump()
        birth_date = deserialize_datetime(profile_dict["birth_date"])
        profile = await add_profile(
            user_id=x_user_id,
            birth_date=birth_date,
            height=profile_dict["height"],
            weight=profile_dict["weight"],
            gender=profile_dict["gender"],
            target_weight=profile_dict["target_weight"],
            daily_step_goal=profile_dict["daily_step_goal"],
        )
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с id {x_user_id} не найден"
            )
        return {"message": "Профиль успешно обнволён", "status": "ok"}
    except HTTPException as e:
        raise e

@router.get("/get_profile", status_code=status.HTTP_200_OK)
async def get_profile(x_user_id: str = Header(default=None, alias="X-User-Id")):
    profile = await get_profile_by_id(user_id=x_user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Профиль пользователя с id {x_user_id} не найден"
        )
    profile_dict = {
            key: serialize_datetime(value) for key, value in profile.items()
        }
    return profile_dict

@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def del_user(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        result = await delete_user(user_id=x_user_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с id {x_user_id} не найден"
            )
        return result
    except HTTPException as e:
        raise e
    

@router.get("/check_user", status_code=status.HTTP_200_OK)
async def check_user(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        user = await get_user_by_id(user_id=x_user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        return {"status": "ok", "user_id": x_user_id}
    except HTTPException as e:
        raise e