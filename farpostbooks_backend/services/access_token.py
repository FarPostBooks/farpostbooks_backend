from datetime import datetime, timedelta
from typing import Any, Dict

from jose import jwt

from farpostbooks_backend.settings import settings


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Создание JWT токена.

    :param data: Данные для JWT токена.
    :return: JWT токен.
    """
    expires_delta = timedelta(minutes=settings.expire_minutes)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
