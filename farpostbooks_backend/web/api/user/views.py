from typing import Optional

from fastapi import APIRouter
from fastapi.param_functions import Depends

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.services.telegram_hash import HashCheck
from farpostbooks_backend.web.api.user.schema import (
    IsTelegramHashValid,
    IsUserExist,
    TelegramUserDTO,
    UserModelDTO,
    UserModelUpdateDTO,
)

router = APIRouter()


@router.get("/telegram_hash", response_model=IsTelegramHashValid)
async def check_telegram_hash(
    telegram_data: TelegramUserDTO = Depends(),
) -> IsTelegramHashValid:
    """
    Проверить валидность Telegram hash'а.

    :param telegram_data: Pydantic модель с данными о пользователе из Telegram.
    :return: Существует ли пользователь True/False
    """
    return IsTelegramHashValid(
        status=HashCheck(
            telegram_data.dict(exclude_none=True),
        ).check_hash(),
    )


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
    status = await user_dao.get_user(telegram_id=telegram_id)
    return IsUserExist(status=bool(status))


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
