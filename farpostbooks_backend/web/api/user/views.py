from fastapi import APIRouter
from fastapi.param_functions import Depends

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.web.api.user.schema import IsUserExist

router = APIRouter()


@router.get("/", response_model=IsUserExist)
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
