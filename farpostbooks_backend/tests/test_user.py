import secrets

import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.services.telegram_hash import HashCheck

fake = Faker(locale="ru_RU", seed=secrets.randbelow(1000))


@pytest.mark.anyio
async def test_exising(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Тест эндпоинта с проверкой существования юзера и правильной работы БД."""
    dao = UserDAO()

    telegram_id = secrets.randbelow(1000000000000)
    await dao.create_user_model(
        telegram_id=telegram_id,
        name=f"{fake.first_name()} {fake.last_name()}",
        position=fake.job(),
        about=fake.sentence(nb_words=20),
    )

    url = fastapi_app.url_path_for("check_existing_user", telegram_id=telegram_id)
    response = await client.get(url)
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["status"]


@pytest.mark.anyio
async def test_updating(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Тест эндпоинта с обновлением данных в БД."""
    dao = UserDAO()

    telegram_id = secrets.randbelow(1000000000000)
    user = await dao.create_user_model(
        telegram_id=telegram_id,
        name=f"{fake.first_name()} {fake.last_name()}",
        position=fake.job(),
        about=fake.sentence(nb_words=20),
    )
    new_name = f"{fake.first_name()} {fake.last_name()}"
    new_position = fake.job()

    url = fastapi_app.url_path_for("update_user", telegram_id=telegram_id)
    response = await client.put(
        url,
        json={
            "name": new_name,
            "position": new_position,
        },
    )
    updated_user = await dao.get_user(telegram_id)

    assert updated_user is not None
    assert updated_user.name == new_name
    assert updated_user.position == new_position
    assert updated_user.about == user.about
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_telegram_hash(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Тест эндпоинта с проверкой Telegram Hash."""
    url = fastapi_app.url_path_for("check_telegram_hash")
    params = {
        "id": "1",
        "first_name": "Pavel",
        "last_name": "Durov",
        "username": "durov",
        "photo_url": "https://t.me/i/userpic/320/durov.jpg",
        "auth_date": "1676457798",
        "hash": "cd1d17e51e620c0aa96a7b1d62a4ca99b936872b45e58a869d81a66661902c72",
    }

    response = await client.get(url, params=params)
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["status"] == HashCheck(params).check_hash()
