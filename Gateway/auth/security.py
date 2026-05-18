from fastapi import Request
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import httpx
from httpx import AsyncClient, AsyncHTTPTransport
from auth.settings import settings
from fastapi import Depends, HTTPException, status
async def get_token_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get("access_token")
    if token:
        return token
    return None

def decode_access_token(token: str) -> dict:
    """
    Декодирует JWT access token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

async def get_current_user(token: str = Depends(get_token_from_request)):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},)
    return user_id
transport = AsyncHTTPTransport(retries=3)
client_auth = AsyncClient(
    base_url="http://localhost:8000",
    timeout=5.0,
    transport=transport
)
async def get_current_admin_user(current_user: str = Depends(get_current_user)):
    try:
        auth_client = await client_auth.get(
            "/auth/is_admin",
            headers={"X-User-Id": f"{current_user}"},
            timeout=3.0
        )
        auth_client.raise_for_status()
        data = auth_client.json()
        is_admin = data["is_admin"]
        if is_admin == False:
            raise HTTPException(status_code=403, detail="У вас нет прав")
        return current_user
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail="Неверный формат данных")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера")
    except KeyError as e:
        raise HTTPException(status_code=400, detail="Неверный формат данных")