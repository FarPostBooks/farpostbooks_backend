import secrets

import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO


@pytest.mark.anyio
async def test_scopes(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта недоступного обычному пользователю."""
    url = fastapi_app.url_path_for("update_user", telegram_id=1)

    response = await user_client.put(
        url,
        json={
            "position": fake.job(),
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_update_user(
    fastapi_app: FastAPI,
    admin_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для обновления данных пользователя в БД."""
    dao = UserDAO()

    telegram_id = secrets.randbelow(1000000000000)
    user = await dao.create_user_model(
        telegram_id=telegram_id,
        name=f"{fake.first_name()} {fake.last_name()}",
        position=fake.job(),
        about=fake.sentence(nb_words=10),
    )
    new_name = f"{fake.first_name()} {fake.last_name()}"
    new_position = fake.job()

    url = fastapi_app.url_path_for("update_user", telegram_id=telegram_id)
    response = await admin_client.put(
        url,
        json={
            "name": new_name,
            "position": new_position,
        },
    )
    updated_user = await dao.get_user(telegram_id)

    assert response.status_code == status.HTTP_200_OK
    assert updated_user is not None
    assert updated_user.name == new_name
    assert updated_user.position == new_position
    assert updated_user.about == user.about


@pytest.mark.anyio
async def test_fail_update_user(
    fastapi_app: FastAPI,
    admin_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для обновления данных пользователя в БД."""
    dao = UserDAO()

    url = fastapi_app.url_path_for(
        "update_user",
        telegram_id=1000,
    )
    response = await admin_client.put(
        url,
        json={
            "name": f"{fake.first_name()} {fake.last_name()}",
            "position": fake.job(),
        },
    )
    updated_user = await dao.get_user(1000)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert updated_user is None
