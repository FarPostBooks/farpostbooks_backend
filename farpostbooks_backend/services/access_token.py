from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.settings import settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user": "Получение данных только для текущего пользователя.",
        "admin": "Получение данных о других пользователях и доступ к админ-панели.",
    },
    scheme_name="JWT",
)


class TokenData(BaseModel):
    """Данные в JWT токене."""

    id: int
    scopes: List[str] = []


def create_access_token(data: Dict[str, Union[Any]]) -> str:
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


def get_auth_value(security_scopes: SecurityScopes) -> str:
    """
    Получение WWW-Authenticate.

    :param security_scopes: данные из security_scopes.
    :return: WWW-Authenticate.
    """
    if security_scopes.scopes:
        return f'Bearer scope="{security_scopes.scope_str}"'
    return "Bearer"


def get_decoded_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """
    Декодирование JWT токена.

    :param token: JWT токен.
    :param credentials_exception: Экземпляр класса ошибки.
    :raises credentials_exception: Вывод ошибки в случае невалидного токена.
    :return: Данные токена.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        telegram_id: Optional[int] = payload.get("sub")
        if telegram_id is None:
            raise credentials_exception
        return TokenData(
            scopes=payload.get("scopes", []),
            id=telegram_id,
        )
    except JWTError as error:
        raise credentials_exception from error


async def get_current_user(
    security_scopes: SecurityScopes,
    user_dao: UserDAO = Depends(),
    token: str = Depends(oauth2_scheme),
) -> UserModel:
    """
    Получение модели пользователя по JWT токену.

    :param security_scopes: Скоупы пользователя.
    :param user_dao: DAO модель пользователя.
    :param token: JWT токен пользователя.
    :raises credentials_exception: Возвращение ошибки, если не удалось получить модель.
    :raises HTTPException: Возвращение ошибки, если у пользователя
                           нет доступа к эндпоинту.

    :return: Модель пользователя.
    """
    authenticate_value = get_auth_value(security_scopes)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось получить данные о пользователе.",
        headers={"WWW-Authenticate": authenticate_value},
    )

    token_data = get_decoded_token(token, credentials_exception)
    user = await user_dao.get_user(token_data.id)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав доступа.",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user
