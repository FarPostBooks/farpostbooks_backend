from datetime import datetime

from tortoise.queryset import Q

from farpostbooks_backend.db.models.userbook_model import UserBookModel


class UserBookDAO:
    """Класс для доступа к таблице истории взятия книг."""

    @staticmethod
    async def get_book(
        user_id: int,
        book_id: int,
    ) -> UserBookModel:
        """
        Взятие книги с полки.

        :param user_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        :return: Модель взятие книги.
        """
        return await UserBookModel.create(
            user=user_id,
            book=book_id,
        )

    @staticmethod
    async def drop_book(
        user_id: int,
        book_id: int,
    ) -> None:
        """
        Отдача киниги обратно на полку.

        :param user_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        """
        await UserBookModel.filter(Q(user=user_id) & Q(book=book_id)).update(
            back_timestamp=datetime.utcnow(),
        )

    @staticmethod
    async def grading(
        user_id: int,
        book_id: int,
        rating: int,
    ) -> None:
        """
        Выставление рейтинга после прочтения.

        :param user_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        :param rating: Оценка книги.
        """
        await UserBookModel.filter(Q(user=user_id) & Q(book=book_id)).update(
            rating=rating,
        )
