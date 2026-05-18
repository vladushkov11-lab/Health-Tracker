from fastapi import APIRouter, status, HTTPException, requests, responses, Header
from api.schemas import SCreateUser, SUserLogin, SUserUpdate
from auth.security import get_password_hash, authenticate_user, create_access_token
from database.dao import add_user, delete_user_dao, get_user_by_id, update_user_dao, is_admin_user, get_user_by_email
import httpx
from sqlalchemy.exc import IntegrityError
from httpx import AsyncClient, AsyncHTTPTransport, HTTPStatusError, RequestError
from api.logging_config import logger
transport = AsyncHTTPTransport(retries=3)
client_auth = AsyncClient(
    base_url="http://app_service:8002",
    timeout=5.0,
    transport=transport
)
router = APIRouter(prefix="/auth")
@router.post("/register", status_code=status.HTTP_201_CREATED) 
async def register(user: SCreateUser):
    try:
        user_dict = user.model_dump()
        email = user_dict["email"]
        if user_dict["password"] != user_dict["password_check"]:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")
        existing_user = await get_user_by_email(email=email)
        if existing_user:
            logger.error(f"Пользователь {email} уже существует в БД (проверка до добавления)")
            raise HTTPException(status_code=409, detail="Пользователь уже существует")
        
        password_hashed = get_password_hash(user_dict["password"])
        
        new_user = await add_user(
            email=user_dict["email"],
            password=password_hashed,
            first_name=user_dict["first_name"],
            last_name=user_dict["last_name"],
            phone_number=user_dict["phone_number"]
        )
        logger.info(f"Результат add_user: {new_user}")
        if new_user is None:
            raise HTTPException(status_code=409, detail="Пользователь уже существует")
        try:
            
            auth_response = await client_auth.post(
                    "/app/create_user",
                    json=new_user,
                    timeout=3.0
                )
            auth_response.raise_for_status()
            data = auth_response.json()
            if data["status"] == "error":
                await delete_user_dao(user_id=new_user["user_id"])
                raise HTTPException(status_code=400, detail="Пользователь уже существует")
            if auth_response.status_code != 201:
                raise HTTPException(status_code=auth_response.status_code, detail=auth_response.json())
            return {"message": "Пользователь успешно зарегистрирован", "status": "ok"}
        except HTTPStatusError as e:
            raise e
    except HTTPException as e:
        raise e
    except IntegrityError as e:
        raise HTTPException(status_code=409, detail="Пользователь уже существует")

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: SUserLogin):
    try:
        user_dict = user.model_dump()
        user = await authenticate_user(email=user_dict["email"], password=user_dict["password"])
        if not user:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
        access_token = create_access_token(data={"sub": user["user_id"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise e

@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан user_id"
            )
        try:
            auth_response = await client_auth.get(
                "/app/check_user",
                headers={"X-User-Id": f"{x_user_id}"},
                timeout=3.0
            )
            data = auth_response.json()
            if data["status"] == "error":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        except HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
        
        
        auth_response = await client_auth.delete(
            "/app/delete_user",
            headers={"X-User-Id": f"{x_user_id}"},
            timeout=3.0
        )
        auth_response.raise_for_status()
        result = await delete_user_dao(user_id=x_user_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return {"message": "Пользователь успешно удален", "status": "ok"}
    except HTTPException as e:
        raise e

@router.patch("/update_user", status_code=status.HTTP_200_OK)
async def upd_user(user: SUserUpdate, x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан user_id"
            )
        user_dict = user.model_dump()
        user = await update_user_dao(user_id=x_user_id, **user_dict)
        if user is None:
            return {"message": "Пользователь не найден", "status": "error"}
        return {"message": "Пользователь успешно обновлен", "status": "ok"}
    except HTTPException as e:
        raise e

@router.get("/get_user", status_code=status.HTTP_200_OK)
async def get_user(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан user_id"
            )
        user = await get_user_by_id(user_id=x_user_id)
        if user is None:
            return {"message": "Пользователь не найден", "status": "error"}
        return user
    except HTTPException as e:
        raise e

@router.get("/is_admin", status_code=status.HTTP_200_OK)
async def is_admin(x_user_id: str = Header(default=None, alias="X-User-Id")):
    try:
        if x_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не указан user_id"
            )
        user = await is_admin_user(user_id=x_user_id)
        if user is None:
            return {"message": "Пользователь не найден", "status": "error"}
        return {"is_admin": user}
    except HTTPException as e:
        raise e