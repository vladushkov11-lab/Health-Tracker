from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from database.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from auth.settings import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:

    if hashed_password.startswith("$2b$"):
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    """
    Создаёт хеш из пароля.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, additional_claims: Optional[dict] = None) -> str:
    """
    Создаёт JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
async def authenticate_user(email: str, password: str):
    """
    Аутентифицирует пользователя по номеру телефона и паролю.
    """
    from database.dao import get_user_by_email
    # 1. Ищем пользователя в базе данных
    user = await get_user_by_email(email=email)
    
    # 2. Если пользователь не найден — возвращаем None
    if not user:
        return None
    
    # 3. Проверяем пароль с обработкой исключений
    try:
        if not verify_password(password, user["password"]):
            return None
    except Exception as e:
        print(f"[DEBUG] Ошибка при проверке пароля: {e}")
        return None
    
    return user
