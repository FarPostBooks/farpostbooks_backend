from typing import List, Optional

from farpostbooks_backend.db.models.book_model import BookModel


class BookDAO:
    """Класс для доступа к таблице книг."""

    @staticmethod
    async def create_book_model(
        isbn_id: int,
        name: str,
        description: str,
        image: str,
    ) -> BookModel:
        """
        Добавить новую книгу.

        :param isbn_id: ISBN номер книги.
        :param name: Название книги.
        :param description: Описание книги.
        :param image: Фотография книги.
        :return: Модель новой книги.
        """
        return await BookModel.create(
            id=isbn_id,
            name=name,
            description=description,
            image=image,
        )

    @staticmethod
    async def delete_book_model(
        isbn_id: int,
    ) -> None:
        """
        Удаление книги.

        :param isbn_id: ISBN номер книги.
        """
        await BookModel.filter(id=isbn_id).delete()

    @staticmethod
    async def search_bok(
        isbn_id: int,
    ) -> Optional[BookModel]:
        """
        Получить информацию о книге по его ISDN.

        :param isbn_id: ISBN номер книги.
        :return: stream of dummies.
        """
        return await BookModel.get_or_none(
            id=isbn_id,
        )

    @staticmethod
    async def list_book(
        limit: int,
        offset: int,
    ) -> List[BookModel]:
        """
        Выгрузка списка книг на главную страницу.

        :param limit: Максимальное количество выгружаемых книг.
        :param offset: Сдвиг от первой книги.
        :return: Список из книг со сдвигом.
        """
        return await BookModel.all().limit(limit).offset(offset)
