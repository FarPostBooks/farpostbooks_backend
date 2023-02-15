from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from jose import JWTError, jwt
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.services.access_token import create_access_token
from farpostbooks_backend.services.telegram_hash import HashCheck
from farpostbooks_backend.settings import settings
from farpostbooks_backend.web.api.user.schema import (
    AuthorizationToken,
    CreateUserDTO,
    IsUserExist,
    TelegramUserDTO,
    TokenData,
    UserModelDTO,
    UserModelUpdateDTO,
    oauth2_scheme,
)

router = APIRouter()


async def get_current_user(
    user_dao: UserDAO = Depends(),
    token: str = Depends(oauth2_scheme),
) -> UserModel:
    """
    Получение модели пользователя по JWT токену.

    :param user_dao: DAO модель пользователя.
    :param token: JWT токен пользователя.
    :raises credentials_exception: Возвращение ошибки, если не удалось получить модель.
    :return: Модель пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось получить данные о пользователе.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        telegram_id: Optional[int] = payload.get("sub")
        if telegram_id is None:
            raise credentials_exception
        token_data = TokenData(id=telegram_id)
    except JWTError:  # noqa: WPS329
        raise credentials_exception from JWTError
    user = await user_dao.get_user(token_data.id)
    if user is None:
        raise credentials_exception
    return user


@router.get("/me", response_model=UserModelDTO)
async def get_me(
    current_user: UserModelDTO = Depends(get_current_user),
) -> UserModelDTO:
    """
    Получение данных о себе, используя сессию.

    :param current_user: Pydantic модель пользователя, полученная по JWT токену.
    :return: Модель с данными о пользователе.
    """
    return current_user


@router.get("/token", response_model=AuthorizationToken)
async def auth_user(
    telegram_data: TelegramUserDTO = Depends(),
    user_dao: UserDAO = Depends(),
) -> AuthorizationToken:
    """
    Проверить валидность Telegram hash'а.

    :param telegram_data: Pydantic модель с данными о пользователе из Telegram.
    :param user_dao: DAO для модели пользователя.
    :raises HTTPException: Возвращение ошибки, если не удалось получить JWT токен.
    :return: access_token для доступа к внутренним эндпоинтам.
    """
    hash_check = HashCheck(
        telegram_data.dict(exclude_none=True),
    )
    if not hash_check.check_hash():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram Hash не валиден.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_dao.get_user(telegram_data.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="Пользователь не зарегистрирован.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return AuthorizationToken(access_token=access_token)


@router.get("/{telegram_id}", response_model=IsUserExist)
async def check_existing_user(
    telegram_id: int,
    user_dao: UserDAO = Depends(),
) -> IsUserExist:
    """
    Проверить существует ли пользователь по его Telegram ID.

    :param telegram_id: Telegram ID пользователя.
    :param user_dao: DAO для модели пользователя.
    :return: Существует ли пользователь True/False
    """
    user = await user_dao.get_user(telegram_id=telegram_id)
    return IsUserExist(status=bool(user))


@router.put("/{telegram_id}", response_model=UserModelDTO)
async def update_user(
    telegram_id: int,
    new_user_data: UserModelUpdateDTO,
    user_dao: UserDAO = Depends(),
) -> Optional[UserModel]:
    """
    Обновить данные пользователя по его Telegram ID.

    :param telegram_id: Telegram ID пользователя.
    :param new_user_data: Pydantic модель с новыми данными о пользователе.
    :param user_dao: DAO для модели пользователя.
    :return: Модель пользователя с измененными данными.
    """
    return await user_dao.change_user_model(telegram_id, new_user_data)


@router.post("/", response_model=AuthorizationToken)
async def create_user(
    user_data: CreateUserDTO,
    user_dao: UserDAO = Depends(),
) -> AuthorizationToken:
    """
    Создание нового пользователя.

    :param user_data: Данные о пользователе.
    :param user_dao: DAO модель пользователя.
    :raises HTTPException: Возвращение ошибки, если не удалось получить JWT токен.
    :return: access_token для доступа к внутренним эндпоинтам.
    """
    hash_check = HashCheck(
        user_data.telegram.dict(exclude_none=True),
    )
    if not hash_check.check_hash():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram Hash не валиден.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_dao.get_user(user_data.telegram.id)
    if user is None:
        user = await user_dao.create_user_model(
            user_data.telegram.id,
            **user_data.user.dict(),
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return AuthorizationToken(access_token=access_token)
