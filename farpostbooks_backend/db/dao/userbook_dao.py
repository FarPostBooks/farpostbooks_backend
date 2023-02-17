from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from starlette import status
from tortoise.queryset import Q

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
        :raises HTTPException: Ошибка, если не удалось взять книгу.
        :return: Модель взятие книги.
        """
        user_already_have_book = await UserBookModel.filter(
            user_id=telegram_id,
            back_timestamp=None,
        ).count()
        if user_already_have_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не может взять несколько книг.",
            )

        another_user_have_book = await UserBookModel.filter(
            book_id=book_id,
            back_timestamp=None,
        ).count()
        if another_user_have_book:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Несколько пользователей не могут взять одну книгу.",
            )

        return await UserBookModel.create(
            user_id=telegram_id,
            book_id=book_id,
        )

    @staticmethod
    async def return_book(
        telegram_id: int,
        book_id: int,
    ) -> None:
        """
        Возвращение книги обратно на полку.

        :param telegram_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        """
        await UserBookModel.filter(
            Q(user_id=telegram_id) & Q(book_id=book_id),
        ).update(
            back_timestamp=datetime.utcnow(),
        )

    @staticmethod
    async def set_rating(
        telegram_id: int,
        book_id: int,
        rating: int,
    ) -> None:
        """
        Выставление рейтинга после прочтения.

        :param telegram_id: Telegram ID пользователя.
        :param book_id: ISBN выбранной книги.
        :param rating: Оценка книги.
        """
        await UserBookModel.filter(
            Q(user_id=telegram_id) & Q(book_id=book_id),
        ).update(
            rating=rating,
        )

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
            )
            .prefetch_related("book")
            .order_by("id")
            .limit(limit)
            .offset(offset)
        )
