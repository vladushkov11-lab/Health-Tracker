import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from fastapi import Request, Response

def set_cookie(access_token: str, response: Response):
    cookie_value = access_token
    response.set_cookie(
        key="access_token",
        value=cookie_value,
        httponly=True,
        max_age=86400,
        domain="",
        path="/",
        secure=False,
        samesite="lax",
    )
    
def clear_session_cookie(response: Response):
    response.delete_cookie(key="access_token",
                            domain="",
                            path="/",)