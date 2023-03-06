import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.dao.userbook_dao import UserBookDAO
from farpostbooks_backend.web.api.enums import FilterFlag


@pytest.mark.anyio
async def test_search_book(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для поиска книги."""
    dao = BookDAO()

    isbn = int(fake.isbn13().replace("-", ""))
    book = await dao.create_book_model(
        book_id=isbn,
        name=fake.sentence(nb_words=5),
        description=fake.sentence(nb_words=5),
        image=fake.image_url(),
        author=fake.name(),
        publish=fake.year(),
    )

    url = fastapi_app.url_path_for("search_book", book_id=isbn)
    response = await user_client.get(url)
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["id"] == book.id
    assert json_response["name"] == book.name
    assert json_response["description"] == book.description
    assert json_response["image"] == book.image


@pytest.mark.anyio
async def test_create_book(
    fastapi_app: FastAPI,
    admin_client: AsyncClient,
) -> None:
    """Тест эндпоинта с добавлением данных о книге в БД."""
    dao = BookDAO()

    isbn = 9785911511036
    url = fastapi_app.url_path_for("create_book", book_id=isbn)
    response = await admin_client.post(url)
    json_response = response.json()
    book = await dao.search_book(isbn)

    assert response.status_code == status.HTTP_200_OK
    assert book is not None
    assert json_response["id"] == book.id
    assert json_response["name"] == book.name
    assert json_response["description"] == book.description


@pytest.mark.anyio
async def test_fail_create_book(
    fastapi_app: FastAPI,
    admin_client: AsyncClient,
) -> None:
    """Тест ошибки эндпоинта с добавлением данных о книге в БД."""
    dao = BookDAO()

    isbn = 1
    url = fastapi_app.url_path_for("create_book", book_id=isbn)
    response = await admin_client.post(url)
    book = await dao.search_book(isbn)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert book is None


@pytest.mark.anyio
async def test_get_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта с получением списка книг."""
    dao = BookDAO()

    isbn = int(fake.isbn13().replace("-", ""))
    url = fastapi_app.url_path_for("get_books")

    response = await user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert not response.json()

    book = await dao.create_book_model(
        book_id=isbn,
        name=fake.sentence(nb_words=5),
        description=fake.sentence(nb_words=5),
        image=fake.image_url(),
        author=fake.name(),
        publish=fake.year(),
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
async def test_get_taken_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта с получением списка взятых книг."""
    book_dao = BookDAO()
    dao = UserBookDAO()

    url = fastapi_app.url_path_for("get_books")

    books = []
    for _ in range(5):
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
    for index in range(2):
        await dao.take_book(telegram_id=2, book_id=books[index].id)

    response = await user_client.get(
        url,
        params={
            "flag": FilterFlag.taken.value,
        },
    )
    books_from_response = response.json()
    books_from_dao = await book_dao.get_books(FilterFlag.taken)
    for book_index, book_from_dao in enumerate(books_from_dao):
        assert books_from_response[book_index]["id"] == book_from_dao.id


@pytest.mark.anyio
async def test_get_not_taken_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта с получением списка не взятых книг."""
    book_dao = BookDAO()
    dao = UserBookDAO()

    url = fastapi_app.url_path_for("get_books")

    books = []
    for _ in range(5):
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
    for index in range(2):
        await dao.take_book(telegram_id=2, book_id=books[index].id)

    response = await user_client.get(
        url,
        params={
            "flag": FilterFlag.not_taken.value,
        },
    )
    books_from_response = response.json()
    books_from_dao = await book_dao.get_books(FilterFlag.not_taken)
    for book_index, book_from_dao in enumerate(books_from_dao):
        assert books_from_response[book_index]["id"] == book_from_dao.id


@pytest.mark.anyio
async def test_not_permitted_member_get_books(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта с получением списка книг с указанием флага не из Enum'а."""
    url = fastapi_app.url_path_for("get_books")

    response = await user_client.get(
        url,
        params={
            "flag": "RANDOM",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
