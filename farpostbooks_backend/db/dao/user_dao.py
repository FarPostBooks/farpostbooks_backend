from typing import Optional

from farpostbooks_backend.db.models.user_model import UserModel


class UserDAO:
    """Класс для доступа к таблице юзеров."""

    @staticmethod
    async def create_user_model(
        telegram_id: int,
        name: str,
        position: str,
        about: str,
    ) -> None:
        """
        Добавить нового пользователя.

        :param telegram_id: Telegram ID.
        :param name: Имя фамилия.
        :param position: Должность.
        :param about: Интересы.
        """
        await UserModel.create(
            id=telegram_id,
            name=name,
            position=position,
            about=about,
        )

    @staticmethod
    async def get_user(
        telegram_id: int,
    ) -> Optional[UserModel]:
        """
        Получить информацию о пользователе по его Telegram ID.

        :param telegram_id: Telegram ID.
        :return: stream of dummies.
        """
        return await UserModel.get_or_none(
            id=telegram_id,
        )
