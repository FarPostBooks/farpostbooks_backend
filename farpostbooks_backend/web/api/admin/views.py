from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.web.api.schema import UserModelDTO, UserModelUpdateDTO

router = APIRouter()


@router.get("/", response_model=UserModelDTO)
async def get_user(
    telegram_id: int,
    _: UserModel = Security(get_current_user, scopes=["admin"]),
    user_dao: UserDAO = Depends(),
) -> UserModel:
    """
    Проверить существует ли пользователь по его Telegram ID.

    :param telegram_id: Telegram ID пользователя.
    :param _: Текущий пользователь по JWT токену.
    :param user_dao: DAO для модели пользователя.
    :raises HTTPException: Пользователь не найден.
    :return: Существует ли пользователь True/False
    """
    user = await user_dao.get_user(telegram_id=telegram_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )
    return user


@router.put("/", response_model=UserModelDTO)
async def update_user(
    telegram_id: int,
    new_user_data: UserModelUpdateDTO,
    _: UserModel = Security(get_current_user, scopes=["admin"]),
    user_dao: UserDAO = Depends(),
) -> Optional[UserModel]:
    """
    Обновить данные пользователя по его Telegram ID.

    :param telegram_id: Telegram ID пользователя.
    :param new_user_data: Pydantic модель с новыми данными о пользователе.
    :param _: Текущий пользователь по JWT токену.
    :param user_dao: DAO для модели пользователя.
    :return: Модель пользователя с измененными данными.
    """
    return await user_dao.change_user_model(telegram_id, new_user_data)
