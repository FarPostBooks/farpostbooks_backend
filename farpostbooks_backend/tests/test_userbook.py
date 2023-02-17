import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO
from farpostbooks_backend.db.models.book_model import BookModel


@pytest.mark.anyio
async def test_get_user_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для скроллинга странички с книгами пользователя."""
    book_dao = BookDAO()
    dao = UserBookDAO()

    isbn = int(fake.isbn13().replace("-", ""))
    book = await book_dao.create_book_model(
        book_id=isbn,
        name=fake.sentence(nb_words=5),
        description=fake.sentence(nb_words=5),
        image=fake.image_url(),
        author=fake.name(),
        publish=fake.year(),
    )
    url = fastapi_app.url_path_for("get_user_books", telegram_id=2)

    response = await user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert not response.json()

    await dao.take_book(
        telegram_id=2,
        book_id=isbn,
    )
    response = await user_client.get(
        url,
        params={
            "limit": 1,
            "offset": 0,
        },
    )
    assert response.json()[0]["id"] == book.id

    response = await user_client.get(url)
    assert response.json()[0]["id"] == book.id


@pytest.mark.anyio
async def test_take_book(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    admin_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для скроллинга странички с книгами пользователя."""
    book_dao = BookDAO()
    dao = UserBookDAO()

    isbn = int(fake.isbn13().replace("-", ""))
    book = await book_dao.create_book_model(
        book_id=isbn,
        name=fake.sentence(nb_words=5),
        description=fake.sentence(nb_words=5),
        image=fake.image_url(),
        author=fake.name(),
        publish=fake.year(),
    )
    url = fastapi_app.url_path_for("take_book", book_id=isbn)

    response = await user_client.post(url)
    assert response.status_code == status.HTTP_200_OK

    user_book: BookModel = (await dao.get_books(telegram_id=2))[0].book
    assert user_book.id == book.id

    response = await user_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await admin_client.post(url)
    assert response.status_code == status.HTTP_409_CONFLICT
