from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.services.access_token import (
    create_access_token,
    get_current_user,
)
from farpostbooks_backend.services.telegram_hash import HashCheck
from farpostbooks_backend.settings import settings
from farpostbooks_backend.web.api.schema import UserModelDTO
from farpostbooks_backend.web.api.user.schema import (
    AuthorizationToken,
    CreateUserDTO,
    TelegramUserDTO,
)

router = APIRouter()


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
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "scopes": [user.status],
        },
    )
    return AuthorizationToken(
        access_token=access_token,
        token_type=settings.token_type,
    )  # noqa: WPS421, S106


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

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "scopes": [user.status],
        },
    )
    return AuthorizationToken(
        access_token=access_token,
        token_type=settings.token_type,
    )  # noqa: WPS421, S106
