from typing import Optional

from fastapi import APIRouter
from fastapi.param_functions import Depends

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.web.api.book.schema import BookModelDTO

router = APIRouter()


@router.post("/books/{book_id}", response_model=BookModelDTO)
async def create_book(
    book_id: int,
    book_dao: BookDAO = Depends(),
) -> Optional[BookModel]:
    """
    Добавляем новую книгу к уже существующим по его ISBN.

    :param book_id: ISBN книги.
    :param book_dao: DAO для модели книги.
    :return: Возвращаем созданную книгу.
    """
    return await book_dao.create_book_model(
        book_id=book_id,
        name="name",
        description="description",
        image="image",
    )


@router.get("/books/{book_id}", response_model=BookModelDTO)
async def search_book(
    book_id: int,
    book_dao: BookDAO = Depends(),
) -> Optional[BookModel]:
    """
    Получение информации о книге по ISBN.

    :param book_id: ISBN книги.
    :param book_dao: DAO для модели книги.
    :return: Возвращаем информацию о книге.
    """
    return await book_dao.search_book(book_id=book_id)
