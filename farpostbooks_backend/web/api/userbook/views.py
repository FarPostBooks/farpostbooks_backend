from typing import List

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO
from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.web.api.schema import (
    BookIntroduction,
    ScrollDTO,
    UserModelDTO,
)
from farpostbooks_backend.web.api.userbook.schema import RatingDTO

router = APIRouter()


@router.post("/me/books/{book_id}")
async def take_book(
    book_id: int,
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> None:
    """
    Взятие книги с полки.

    :param book_id: ISBN книги.
    :param current_user: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг юзера.
    """
    await user_book_dao.take_book(
        telegram_id=current_user.id,
        book_id=book_id,
    )


@router.get("/{telegram_id}/books", response_model=List[BookIntroduction])
async def get_user_books(
    scroll_dto: ScrollDTO = Depends(),
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> List[BookModel]:
    """
    Получение информации об общем списке книг.

    :param scroll_dto: DTO для работы со скроллингом.
    :param current_user: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг.
    :return: Список книг.
    """
    user_books = await user_book_dao.get_books(
        current_user.id,
        **scroll_dto.dict(exclude_none=True),
    )
    return [user_book.book for user_book in user_books]


@router.put("/me/books/{book_id}")
async def return_book(
    book_id: int,
    rating_dto: RatingDTO,
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> None:
    """
    Возврат книги обратно на полку.

    :param book_id: ISBN книги.
    :param rating_dto: DTO рейтинга книги.
    :param current_user: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг юзера.
    :raises HTTPException: Ошибка, если книгу нельзя вернуть пользователем.
    """
    book = await user_book_dao.get_book(
        telegram_id=current_user.id,
        book_id=book_id,
    )
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя вернуть книгу, которую пользователь ещё не взял.",
        )
    await user_book_dao.return_book(
        telegram_id=current_user.id,
        book_id=book_id,
        **rating_dto.dict(),
    )
