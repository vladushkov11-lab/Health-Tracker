from fastapi import APIRouter, HTTPException, status, Depends, Response, Request, Path
from auth.cookie import set_cookie, clear_session_cookie
from auth.security import decode_access_token, get_current_user, get_current_admin_user
import httpx
from httpx import AsyncClient, AsyncHTTPTransport, HTTPStatusError, RequestError
from api.schemas import SUserLogin, SUserRegister, SUserUpdate
import logging
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")
# Пул соединений для переиспользования клиента
transport = AsyncHTTPTransport(retries=3)
client_auth = AsyncClient(
    base_url="http://auth_service:8000",
    timeout=5.0,
    transport=transport
)
# Хелперы для обработки ошибок
async def handle_httpx_error(e: HTTPStatusError, default_code: int = 500) -> HTTPException:
    status_code = e.response.status_code if e.response else default_code
    logger.error(f"HTTP error from auth service: {e.response.status_code} - {e.response.text}")
    
    if status_code == 401:
        return HTTPException(status_code=401, detail="Неверные данные")
    elif status_code == 404:
        return HTTPException(status_code=404, detail="Ресурс не найден")
    else:
        return HTTPException(status_code=default_code, detail="Ошибка сервиса аутентификации")

async def handle_request_error(e: RequestError) -> HTTPException:
    logger.error(f"Request error to auth service: {e}")
    return HTTPException(status_code=503, detail="Сервис аутентификации недоступен")

def handle_key_error(e: KeyError) -> HTTPException:
    logger.error(f"KeyError parsing response: {e}")
    return HTTPException(status_code=400, detail="Неверный формат данных")

# Эндпоинты для AUth service 

@router.post("/register")
async def register_user(user_data: SUserRegister, response: Response):
    try:
        auth_response = await client_auth.post(
            "/auth/register",
            json=user_data.model_dump(),
            timeout=3.0
        )
        auth_response.raise_for_status()
        data = auth_response.json()
        logger.info(f"User registered successfully: {user_data.email}")
        return {"message": data["message"], "status": "ok"}
    except HTTPStatusError as e:
        if e.response.status_code == 409:
            raise HTTPException(status_code=409, detail="Пользователь уже существует")
        raise await handle_httpx_error(e, 400)
    except RequestError as e:
        raise await handle_request_error(e)
    except KeyError as e:
        raise handle_key_error(e)
@router.post("/login")
async def login_user(user_data: SUserLogin, response: Response):
    try:
        auth_response = await client_auth.post(
            "/auth/login",
            json=user_data.model_dump(),
            timeout=3.0
        )
        auth_response.raise_for_status()
        data = auth_response.json()
        token = data["access_token"]
        
        set_cookie(access_token=token, response=response)
        logger.info(f"User logged in successfully: {user_data.email}")
        return {"message": "Авторизация прошла успешно", "status": "ok"}
    except HTTPStatusError as e:
        raise await handle_httpx_error(e, 401)
    except RequestError as e:
        raise await handle_request_error(e)
    except KeyError as e:
        raise handle_key_error(e)

@router.get("/me")
async def get_user_me(request: Request, current_id: str = Depends(get_current_user)):
    logger.info(f"Fetching user data for id: {current_id}")
    try:
        auth_response = await client_auth.get(
            "/auth/get_user",
            headers={"X-User-Id": f"{current_id}"},
            timeout=3.0
        )
        data = auth_response.json()
        return data
    except HTTPStatusError as e:
        raise await handle_httpx_error(e, 401)
    except RequestError as e:
        raise await handle_request_error(e)
    except KeyError as e:
        raise handle_key_error(e)
    
@router.get("/logout")
async def logout_user(response: Response):
    logger.info("User logout request")
    try:
        clear_session_cookie(response)
        return {"message": "Вы успешно вышли", "status": "ok"}
    except HTTPException as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при выходе")

@router.delete("/delete_user")
async def delete_user(request: Request, user_id: str = Depends(get_current_user)):
    try:
        auth_response = await client_auth.delete(
            "/auth/delete_user",
            headers={"X-User-Id": f"{user_id}"},
            timeout=3.0
        )
        auth_response.raise_for_status()
        data = auth_response.json()
        if data is None:
            return {"message": "Пользователь не найден", "status": "error"}
        logger.info(f"User deleted successfully: {user_id}")
        return {"message": "Пользователь успешно удален", "status": "ok"}
    except HTTPStatusError as e:
        raise await handle_httpx_error(e, 401)
    except RequestError as e:
        raise await handle_request_error(e)
    except KeyError as e:
        raise handle_key_error(e)

@router.patch("/update_user")
async def upd_user(user: SUserUpdate, x_user_id: str = Depends(get_current_user)):
    logger.info(f"Update user request for id: {x_user_id}")
    try:
        user_dict = user.model_dump(exclude_unset=True)
        auth_response = await client_auth.patch(
            "/auth/update_user",
            headers={"X-User-Id": f"{x_user_id}"},
            json=user_dict,
            timeout=3.0
        )
        auth_response.raise_for_status()
        logger.info(f"User updated successfully: {x_user_id}")
        return {"message": "Пользователь успешно обновлен", "status": "ok"}
    except HTTPStatusError as e:
        raise await handle_httpx_error(e, 401)
    except RequestError as e:
        raise await handle_request_error(e)
    except KeyError as e:
        raise handle_key_error(e)
