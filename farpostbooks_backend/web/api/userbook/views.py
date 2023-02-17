from typing import Optional

from fastapi import APIRouter, Depends

from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO
from farpostbooks_backend.db.models.userbook_model import UserBookModel
from farpostbooks_backend.services.access_token import get_current_user
from farpostbooks_backend.web.api.schema import ScrollDTO, UserModelDTO
from farpostbooks_backend.web.api.userbook.schema import UserBookIntroduction, UserBooks

router = APIRouter()


@router.post("/me/books/{book_id}")
async def take_book(
    book_id: int,
    current_user: UserModelDTO = Depends(get_current_user),
    user_book_dao: UserBookDAO = Depends(),
) -> None:
    """
    Получение информации об общем списке книг.

    :param book_id: ISBN книги.
    :param current_user: Текущий пользователь по JWT токену.
    :param user_book_dao: DAO для модели книг юзера.
    """
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
    Получение списка книг пользователя.

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
    Получение списка книг пользователя.

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
