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
    Fixture that creates client for requesting server.

    :param anyio_backend: anyio_backend
    :return: Экземпляр класса для создания фейковых данных.
    """
    return Faker(locale="ru_RU", seed=secrets.randbelow(1000))


@pytest.fixture(autouse=True)
async def initialize_db() -> AsyncGenerator[None, None]:
    """
    Initialize models and database.

    :yields: Nothing.
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
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :param anyio_backend: anyio_backend
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates admin for requesting server.

    :param fastapi_app: the application.
    :param anyio_backend: anyio_backend
    :yield: admin_client for the app.
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
