from typing import List, Optional

from fastapi import APIRouter, Depends

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.web.api.book.schema import (
    BookIntroduction,
    BookModelDTO,
    ScrollDTO,
)

router = APIRouter()


@router.post("/{book_id}", response_model=BookModelDTO)
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
        author="author",
        publish="2022",
    )


@router.get("/{book_id}", response_model=BookModelDTO)
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


@router.get("/", response_model=List[BookIntroduction])
async def get_books(
    scroll_dto: ScrollDTO = Depends(),
    book_dao: BookDAO = Depends(),
) -> List[BookModel]:
    """
    Получение информации об общем списке книг.

    :param scroll_dto: DTO для работы со скроллингом.
    :param book_dao: DAO для модели книги.
    :return: Возвращаем список книг.
    """
    return await book_dao.get_books(**scroll_dto.dict(exclude_unset=True))
