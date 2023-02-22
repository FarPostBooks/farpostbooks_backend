from datetime import datetime
from typing import List, Optional

from farpostbooks_backend.db.models.userbook_model import UserBookModel


class UserBookDAO:
    """Класс для доступа к таблице истории взятия книг."""

    @staticmethod
    async def take_book(
        telegram_id: int,
        book_id: int,
    ) -> Optional[UserBookModel]:
        """
        Взятие книги с полки.

        :param telegram_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        :return: Модель взятие книги.
        """
        return await UserBookModel.create(
            user_id=telegram_id,
            book_id=book_id,
        )

    @staticmethod
    async def check_unreturned_books(
        telegram_id: int,
    ) -> int:
        """
        Наличие не возвращенных книг у пользователя.

        :param telegram_id: Telegram ID пользователя.
        :return: Есть ли у пользователя книга.
        """
        return bool(
            await UserBookModel.filter(
                user_id=telegram_id,
                back_timestamp=None,
            ).count(),
        )

    @staticmethod
    async def check_book_availability(
        book_id: int,
    ) -> bool:
        """
        Наличие книги у пользователей.

        :param book_id: ISBN книги.
        :return: Есть ли книга у кого-то из пользователей.
        """
        return bool(
            await UserBookModel.filter(
                book_id=book_id,
                back_timestamp=None,
            ).count(),
        )

    @staticmethod
    async def return_book(
        telegram_id: int,
        rating: int,
    ) -> None:
        """
        Возвращение книги обратно на полку.

        :param telegram_id: Telegram ID пользователя.
        :param rating: Рейтинг книги.
        """
        await UserBookModel.filter(
            user_id=telegram_id,
            back_timestamp__isnull=True,
        ).update(
            back_timestamp=datetime.utcnow(),
            rating=rating,
        )

    @staticmethod
    async def get_unreturned_book(
        telegram_id: int,
    ) -> Optional[UserBookModel]:
        """
        Получение текущей читаемой книги, если она существует.

        :param telegram_id: Telegram ID пользователя.
        :return: Текущая книга, если существует.
        """
        return await UserBookModel.get_or_none(
            user_id=telegram_id,
            back_timestamp=None,
        ).prefetch_related("book")

    @staticmethod
    async def get_books(
        telegram_id: int,
        limit: int = 10,
        offset: int = 0,
    ) -> List[UserBookModel]:
        """
        Выгрузка списка книг на главную страницу.

        :param telegram_id: Telegram ID пользователя.
        :param limit: Максимальное количество выгружаемых книг.
        :param offset: Сдвиг от первой книги.
        :return: Список из книг со сдвигом.
        """
        return (
            await UserBookModel.filter(
                user_id=telegram_id,
                back_timestamp__isnull=False,
            )
            .prefetch_related("book")
            .order_by("id")
            .limit(limit)
            .offset(offset)
        )

    @staticmethod
    async def get_user_book(
        telegram_id: int,
        book_id: int,
    ) -> Optional[UserBookModel]:
        """
        Выгрузка одной книги.

        :param telegram_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        :return: Модель взятие книги.
        """
        return await UserBookModel.get_or_none(
            user_id=telegram_id,
            book_id=book_id,
        )
