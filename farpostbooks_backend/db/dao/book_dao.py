from datetime import datetime, timedelta
from typing import List, Optional

from tortoise.expressions import Q
from tortoise.functions import Count
from tortoise.queryset import QuerySet

from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.web.api.enums import FilterFlag


class BookDAO:
    """Класс для доступа к таблице книг."""

    @staticmethod
    async def create_book_model(
        book_id: int,
        name: str,
        description: str,
        image: str,
        author: str,
        publish: str,
    ) -> BookModel:
        """
        Добавление новой книги.

        :param book_id: ISBN книги.
        :param name: Название книги.
        :param description: Описание книги.
        :param image: Фотография книги.
        :param author: Авторы книги.
        :param publish: Дата публикации книги.
        :return: Модель новой книги.
        """
        return (
            await BookModel.get_or_create(
                id=book_id,
                name=name,
                description=description,
                image=image,
                author=author,
                publish=publish,
            )
        )[0]

    @staticmethod
    async def delete_book_model(
        isbn: int,
    ) -> None:
        """
        Удаление книги.

        :param isbn: ISBN номер книги.
        """
        await BookModel.filter(id=isbn).delete()

    @staticmethod
    async def search_book(
        book_id: int,
    ) -> Optional[BookModel]:
        """
        Получить информацию о книге по его ISBN.

        :param book_id: ISBN книги.
        :return: stream of dummies.
        """
        return await BookModel.get_or_none(
            id=book_id,
        ).prefetch_related("user_books")

    @staticmethod
    async def get_books(
        flag: FilterFlag = FilterFlag.all,
        limit: int = 10,
        offset: int = 0,
    ) -> List[BookModel]:
        """
        Выгрузка списка книг для выдачи на главной странице.

        :param flag: Фильтр для выдачи списка книг.
        :param limit: Максимальное количество выгружаемых книг.
        :param offset: Сдвиг от первой книги.
        :return: Список из книг со сдвигом.
        """
        books_qs: QuerySet[BookModel] = BookModel.all()
        if flag == FilterFlag.taken:
            books_qs = books_qs.filter(
                user_books__isnull=False,
                user_books__back_timestamp__isnull=True,
            )
        if flag == FilterFlag.not_taken:
            books_qs = books_qs.annotate(
                count_user_books=Count(
                    "user_books",
                    _filter=Q(user_books__back_timestamp__isnull=True),
                ),
            ).filter(
                Q(count_user_books=0),
            )
        return (
            await books_qs.distinct()
            .prefetch_related("user_books")
            .all()
            .limit(limit)
            .offset(offset)
        )

    @staticmethod
    async def get_new_books() -> List[BookModel]:
        """
        Получить список новых книг, которые были добавлены в течение недели.

        :return: Список книг.
        """
        date = datetime.utcnow() - timedelta(weeks=1)
        return await BookModel.filter(
            Q(added_timestamp__gt=date),
        ).all()
