from typing import Optional

from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.web.api.user.schema import UserModelUpdateDTO


class UserDAO:
    """Класс для доступа к таблице юзеров."""

    @staticmethod
    async def create_user_model(
        telegram_id: int,
        name: str,
        position: str,
        about: str,
        status: str = "user",
    ) -> UserModel:
        """
        Добавление нового пользователя.

        :param telegram_id: Telegram ID.
        :param name: Имя фамилия.
        :param position: Должность.
        :param about: Интересы.
        :param status: Статус пользователя для скоупов user/admin.
        :return: Модель нового пользователя.
        """
        return await UserModel.create(
            id=telegram_id,
            status=status,
            name=name,
            position=position,
            about=about,
        )

    @staticmethod
    async def get_user(
        telegram_id: int,
    ) -> Optional[UserModel]:
        """
        Получение информации о пользователе по его Telegram ID.

        :param telegram_id: Telegram ID.
        :return: Объект пользователя, если он существует.
        """
        return await UserModel.get_or_none(
            id=telegram_id,
        )

    async def change_user_model(
        self,
        telegram_id: int,
        new_user_data: UserModelUpdateDTO,
    ) -> Optional[UserModel]:
        """
        Изменение информации о пользователе по его Telegram ID.

        :param telegram_id: Telegram ID.
        :param new_user_data: Pydantic модель для сохранения новых данных.
        :return: Модель пользователя с измененными данными.
        """
        await UserModel.filter(id=telegram_id).update(
            **new_user_data.dict(exclude_unset=True),
        )
        return await self.get_user(telegram_id=telegram_id)
