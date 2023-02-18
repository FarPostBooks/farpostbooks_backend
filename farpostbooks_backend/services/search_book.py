from typing import Any, Dict, Optional

import aiofiles
import httpx

from farpostbooks_backend.settings import settings
from farpostbooks_backend.web.api.schema import BookModelDTO


async def get_books(client: httpx.AsyncClient, isbn: int) -> Dict[Any, Any]:
    """
    Получить информацию о книге по ISBN.

    :param client: Клиент для запросов к серверу.
    :param isbn: ISBN книги.
    :return: Информация о книге.
    """
    try:
        response = await client.get(
            settings.google_books_url,
            params={
                "q": f"isbn:{isbn}",
                "key": settings.google_api_key,
            },
        )
        return response.json()
    except httpx.ConnectTimeout:
        return await get_books(client, isbn)


async def save_thumbnail(
    client: httpx.AsyncClient,
    isbn: int,
    book: Dict[str, Any],
) -> str:
    """
    Сохранение обложки книги.

    :param client: Клиент для запросов к серверу.
    :param isbn: ISBN книги.
    :param book: Данные о книге от Google Books API.
    :return: file_name сохраненного изображения.
    """
    if "imageLinks" not in book:
        image = "not_found.jpeg"
    else:
        thumbnail = book["imageLinks"]["thumbnail"].replace("zoom=1", "zoom=3")

        response = await client.get(thumbnail)
        async with aiofiles.open(f"images/{isbn}.jpeg", mode="wb") as file:
            await file.write(response.read())

        image = f"{isbn}.jpeg"
    return image


async def search_google_books(isbn: int) -> Optional[BookModelDTO]:
    """
    Поиск книги в Google Books API по ISBN.

    :param isbn: ISBN искомой книги.
    :return: Pydantic модель с данными о книге, если она найдена.
    """
    async with httpx.AsyncClient() as client:
        books = await get_books(client, isbn)
        if not books["totalItems"]:
            return None

        book = books["items"][0]["volumeInfo"]
        thumbnail = await save_thumbnail(client, isbn, book)
    return BookModelDTO(
        id=isbn,
        name=book["title"],
        description=book["description"],
        image=thumbnail,
        author=", ".join(book["authors"]),
        publish=book["publishedDate"],
    )
