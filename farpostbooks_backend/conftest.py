import secrets
from typing import Any, AsyncGenerator

import nest_asyncio
import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient, Headers
from tortoise import Tortoise
from tortoise.contrib.test import finalizer, initializer

from farpostbooks_backend.db.config import MODELS_MODULES, TORTOISE_CONFIG
from farpostbooks_backend.settings import settings
from farpostbooks_backend.web.application import get_app

nest_asyncio.apply()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture
def fake(
    anyio_backend: Any,
) -> Faker:
    """
    Создание экземпляра класса для создания фековых данных.

    :param anyio_backend: anyio_backend.
    :return: Экземпляр класса для создания фейковых данных.
    """
    return Faker(locale="ru_RU", seed=secrets.randbelow(1000))


@pytest.fixture(autouse=True)
async def initialize_db() -> AsyncGenerator[None, None]:
    """
    Инициализация моделей и базы данных.

    :yields: Ничего.
    """
    initializer(
        MODELS_MODULES,
        db_url=str(settings.db_url),
        app_label="models",
    )
    await Tortoise.init(config=TORTOISE_CONFIG)

    yield

    await Tortoise.close_connections()
    finalizer()


@pytest.fixture
def fastapi_app() -> FastAPI:
    """
    Фикстура для создания FastAPI приложения.

    :return: Приложение FastAPI с фиктивными зависимостями.
    """
    application = get_app()
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура, создающая клиента для запроса к серверу.

    :param fastapi_app: FastAPI приложение.
    :param anyio_backend: anyio_backend
    :yield: Клиент для приложения.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user_client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура, создающая авторизированного клиента для запроса к серверу.

    :param fastapi_app: FastAPI приложение.
    :param anyio_backend: anyio_backend.
    :yield: Юзер клиент для приложения.
    """
    from farpostbooks_backend.db.dao.user_dao import UserDAO
    from farpostbooks_backend.services.access_token import create_access_token

    dao = UserDAO()

    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        user = await dao.create_user_model(
            telegram_id=2,
            name="user",
            position="user",
            about="user",
        )
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "scopes": [user.status],
            },
        )
        ac.headers = Headers({"Authorization": f"Bearer {access_token}"})
        yield ac


@pytest.fixture
async def admin_client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура, создающая клиента с правами администратора для запроса к серверу.

    :param fastapi_app: FastAPI приложение.
    :param anyio_backend: anyio_backend.
    :yield: Админ клиент для приложения.
    """
    from farpostbooks_backend.db.dao.user_dao import UserDAO
    from farpostbooks_backend.services.access_token import create_access_token

    dao = UserDAO()

    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        user = await dao.create_user_model(
            telegram_id=1,
            name="admin",
            position="admin",
            about="admin",
            status="admin",
        )
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "scopes": [user.status],
            },
        )
        ac.headers = Headers({"Authorization": f"Bearer {access_token}"})
        yield ac
