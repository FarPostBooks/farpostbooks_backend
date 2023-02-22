import secrets

import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO


@pytest.mark.anyio
async def test_get_user_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта со списком книг пользователя."""
    book_dao = BookDAO()
    dao = UserBookDAO()
    url = fastapi_app.url_path_for("get_user_books", telegram_id=2)

    books = []
    for _ in range(2):
        isbn = int(fake.isbn13().replace("-", ""))
        books.append(
            await book_dao.create_book_model(
                book_id=isbn,
                name=fake.sentence(nb_words=5),
                description=fake.sentence(nb_words=5),
                image=fake.image_url(),
                author=fake.name(),
                publish=fake.year(),
            ),
        )

    response = await user_client.get(url)
    user_books = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert (not user_books["books"]) and (user_books["current"] is None)

    await dao.take_book(telegram_id=2, book_id=books[0].id)
    await dao.return_book(telegram_id=2, rating=5)
    await dao.take_book(telegram_id=2, book_id=books[1].id)

    response = await user_client.get(url)
    user_books = response.json()
    user_book_id = user_books["books"][0]["book"]["id"]

    assert user_books["current"]["book"]["id"] == books[1].id
    assert user_book_id == books[0].id


@pytest.mark.anyio
async def test_take_book(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    admin_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для взятия книги с полки пользователем."""
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

    user_book = await dao.get_unreturned_book(telegram_id=2)
    assert user_book is not None
    assert user_book.book.id == book.id

    response = await user_client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await admin_client.post(url)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.anyio
async def test_return_book(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для возвращения книги пользователем."""
    book_dao = BookDAO()
    dao = UserBookDAO()

    isbn = int(fake.isbn13().replace("-", ""))
    rating = secrets.choice(range(1, 6))
    await book_dao.create_book_model(
        book_id=isbn,
        name=fake.sentence(nb_words=5),
        description=fake.sentence(nb_words=5),
        image=fake.image_url(),
        author=fake.name(),
        publish=fake.year(),
    )

    await dao.take_book(
        telegram_id=2,
        book_id=isbn,
    )

    url = fastapi_app.url_path_for("return_book")

    response = await user_client.put(
        url,
        json={
            "rating": rating,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    response = await user_client.put(
        url,
        json={
            "rating": rating,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
