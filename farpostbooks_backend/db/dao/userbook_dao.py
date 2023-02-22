from datetime import datetime
from typing import List, Optional

from farpostbooks_backend.db.models.book_model import BookModel
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
    async def get_books_count_by_user(
        telegram_id: int,
    ) -> int:
        """
        Взятие нескольких книг для одного пользователя.

        :param telegram_id: Telegram ID пользователя.
        :return: Количество взятых книг.
        """
        return await UserBookModel.filter(
            user_id=telegram_id,
            back_timestamp=None,
        ).count()

    @staticmethod
    async def get_users_count_by_book(
        book_id: int,
    ) -> int:
        """
        Взятие одной книги для нескольких пользователей.

        :param book_id: ISBN выбранной книги.
        :return: Количество взитий книги.
        """
        return await UserBookModel.filter(
            book_id=book_id,
            back_timestamp=None,
        ).count()

    @staticmethod
    async def check_book_exist(
        book_id: int,
    ) -> Optional[BookModel]:
        """
        Существование книги по ISBN.

        :param book_id: ISBN выбранной книги.
        :return: Модель искоемой книги.
        """
        return await BookModel.get_or_none(id=book_id)

    @staticmethod
    async def return_book(
        telegram_id: int,
        book_id: int,
        rating: int,
    ) -> None:
        """
        Возвращение книги обратно на полку.

        :param rating: Рейтинг книги.
        :param telegram_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        """
        await UserBookModel.filter(
            user_id=telegram_id,
            book_id=book_id,
        ).update(
            back_timestamp=datetime.utcnow(),
            rating=rating,
        )

    @staticmethod
    async def get_current_book(
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
    async def get_book(
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
            back_timestamp=None,
        )
