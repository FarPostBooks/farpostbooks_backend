from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette import status
from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.db.models.user_model import UserModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.services.search_book import search_google_books
from farpostbooks_backend.web.api.book.schema import BooksDTO
from farpostbooks_backend.web.api.schema import (
    BookIntroduction,
    BookModelDTO,
    UserModelDTO,
)

router = APIRouter(redirect_slashes=False)


@router.post("/{book_id}/", response_model=BookModelDTO)
async def create_book(
    book_id: int,
    _: UserModel = Security(get_current_user, scopes=["admin"]),
    book_dao: BookDAO = Depends(),
) -> PydanticModel:
    """
    Добавление новой книги по ISBN.

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

    json_book = book.dict(exclude_none=True)
    json_book["book_id"] = json_book.pop("id")
    new_book = await book_dao.create_book_model(**json_book)
    return await pydantic_model_creator(BookModel).from_tortoise_orm(new_book)


@router.get("/{book_id}", response_model=BookModelDTO)
async def search_book(
    book_id: int,
    _: UserModelDTO = Depends(get_current_user),
    book_dao: BookDAO = Depends(),
) -> Union[BookModelDTO, PydanticModel]:
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
        return await pydantic_model_creator(BookModel).from_tortoise_orm(book)

    new_book = await search_google_books(book_id)
    if new_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена.",
        )
    return new_book


@router.get("/", response_model=List[BookIntroduction])
async def get_books(
    books_dto: BooksDTO = Depends(),
    _: UserModelDTO = Depends(get_current_user),
    book_dao: BookDAO = Depends(),
) -> List[BookModel]:
    """
    Общий список книг (ограничен по limit/offset).

    :param _: Текущий пользователь по JWT токену.
    :param books_dto: DTO для запроса списка книг.
    :param book_dao: DAO для модели книги.
    :return: Возвращаем список книг.
    """
    return await book_dao.get_books(**books_dto.dict(exclude_none=True))
