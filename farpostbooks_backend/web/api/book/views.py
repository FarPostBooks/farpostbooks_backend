from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette import status

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.services.search_book import search_google_books
from farpostbooks_backend.web.api.book.schema import (
    BookIntroduction,
    BookModelDTO,
    CreateBookModelDTO,
    ScrollDTO,
)
from farpostbooks_backend.web.api.schema import UserModelDTO

router = APIRouter()


@router.post("/{book_id}", response_model=BookModelDTO)
async def create_book(
    book_id: int,
    _: UserModel = Security(get_current_user, scopes=["admin"]),
    book_dao: BookDAO = Depends(),
) -> Optional[BookModel]:
    """
    Добавляем новую книгу к уже существующим по её ISBN.

    :param book_id: ISBN книги.
    :param _: Текущий пользователь по JWT токену.
    :param book_dao: DAO для модели книги.
    :raises HTTPException: Ошибка, если книга не найдена.
    :return: Возвращаем созданную книгу.
    """
    book = await search_google_books(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )
    book_to_create = CreateBookModelDTO(**book.dict(exclude_none=True))
    return await book_dao.create_book_model(**book_to_create.dict(exclude_none=True))


@router.get("/{book_id}", response_model=BookModelDTO)
async def search_book(
    book_id: int,
    _: UserModelDTO = Depends(get_current_user),
    book_dao: BookDAO = Depends(),
) -> Union[BookModel, BookModelDTO]:
    """
    Получение информации о книге по ISBN.

    :param book_id: ISBN книги.
    :param _: Текущий пользователь по JWT токену.
    :param book_dao: DAO для модели книги.
    :raises HTTPException: Ошибка, если книга не найдена.
    :return: Возвращаем информацию о книге.
    """
    book = await book_dao.search_book(book_id=book_id)
    if book is not None:
        return book

    new_book = await search_google_books(book_id)
    if new_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )
    return new_book


@router.get("/", response_model=List[BookIntroduction])
async def get_books(
    scroll_dto: ScrollDTO = Depends(),
    _: UserModelDTO = Depends(get_current_user),
    book_dao: BookDAO = Depends(),
) -> List[BookModel]:
    """
    Получение информации об общем списке книг.

    :param _: Текущий пользователь по JWT токену.
    :param scroll_dto: DTO для работы со скроллингом.
    :param book_dao: DAO для модели книги.
    :return: Возвращаем список книг.
    """
    return await book_dao.get_books(**scroll_dto.dict(exclude_none=True))
