from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO
from farpostbooks_backend.db.models.userbook_model import UserBookModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.web.api.schema import ScrollDTO, UserModelDTO
from farpostbooks_backend.web.api.userbook.schema import (
    RatingDTO,
    UserBookIntroduction,
    UserBooks,
)

router = APIRouter()


@router.post("/me/books/{book_id}")
async def take_book(
    book_id: int,
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> None:
    """
    Взятие книги по ISBN.

    :param book_id: ISBN книги.
    :param current_user: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг юзера.
    :raises HTTPException: Ошибка, если не удалось взять книгу.
    """
    is_exist = await user_book_dao.check_book_exist(book_id=book_id)
    if is_exist is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не может взять несуществующую книгу.",
        )

    user_already_have_book = await user_book_dao.get_books_count_by_user(
        telegram_id=current_user.id,
    )
    if user_already_have_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не может взять несколько книг.",
        )

    another_user_have_book = await user_book_dao.get_users_count_by_book(
        book_id=book_id,
    )
    if another_user_have_book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Несколько пользователей не могут взять одну книгу.",
        )

    await user_book_dao.take_book(
        telegram_id=current_user.id,
        book_id=book_id,
    )


@router.get("/{telegram_id}/books", response_model=UserBooks)
async def get_user_books(
    telegram_id: int,
    scroll_dto: ScrollDTO = Depends(),
    _: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> UserBooks:
    """
    Общий список книг + текущая книга пользователя по Telegram ID.

    (ограничен по limit/offset).

    :param telegram_id: Telegram ID пользователя.
    :param scroll_dto: DTO для работы со скроллингом.
    :param _: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг.
    :return: Список книг.
    """
    return UserBooks(
        current=await user_book_dao.get_current_book(telegram_id),
        books=await user_book_dao.get_books(
            telegram_id=telegram_id,
            **scroll_dto.dict(exclude_none=True),
        ),
    )


@router.get("/{telegram_id}/books/{book_id}", response_model=UserBookIntroduction)
async def get_user_book(
    telegram_id: int,
    book_id: int,
    _: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> Optional[UserBookModel]:
    """
    Подробная информация о книге пользователя по Telegram ID и ISBN.

    :param telegram_id: Telegram ID пользователя.
    :param book_id: ISBN книги.
    :param _: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг.
    :return: Список книг.
    """
    return await user_book_dao.get_book(
        telegram_id=telegram_id,
        book_id=book_id,
    )


@router.put("/me/books/{book_id}")
async def return_book(
    book_id: int,
    rating_dto: RatingDTO,
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> None:
    """
    Обновление информации о книге при возвращении пользователем (timestamp, rating).

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
