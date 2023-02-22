import secrets
import time
from datetime import datetime

import pytest
from faker import Faker
from fastapi import FastAPI
from httpx import AsyncClient
from jose import jwt
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.services.telegram_hash import HashCheck
from farpostbooks_backend.settings import settings


@pytest.mark.anyio
async def test_auth_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта авторизации."""
    dao = UserDAO()
    url = fastapi_app.url_path_for("auth_user")

    simple_profile = fake.simple_profile()
    telegram_id = secrets.randbelow(1000000000000)
    params = {
        "id": str(telegram_id),
        "first_name": simple_profile["name"],
        "username": simple_profile["username"],
        "photo_url": fake.image_url(),
        "auth_date": int(time.mktime(datetime.utcnow().timetuple())),
    }
    params["hash"] = HashCheck(params).calc_hash()

    response = await client.get(url, params=params)
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT

    await dao.create_user_model(
        telegram_id=telegram_id,
        name=f"{fake.first_name()} {fake.last_name()}",
        position=fake.job(),
        about=fake.sentence(nb_words=10),
    )
    response = await client.get(url, params=params)
    json_response = response.json()
    payload = jwt.decode(
        json_response["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm],
    )

    assert response.status_code == status.HTTP_200_OK
    assert params["id"] == payload.get("sub")


@pytest.mark.anyio
async def test_create_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для создания нового пользователя."""
    dao = UserDAO()
    url = fastapi_app.url_path_for("create_user")

    simple_profile = fake.simple_profile()
    telegram_id = secrets.randbelow(1000000000000)
    params = {
        "id": str(telegram_id),
        "first_name": simple_profile["name"],
        "username": simple_profile["username"],
        "photo_url": fake.image_url(),
        "auth_date": int(time.mktime(datetime.utcnow().timetuple())),
    }
    params["hash"] = HashCheck(params).calc_hash()

    name = f"{fake.first_name()} {fake.last_name()}"
    position = fake.job()
    about = fake.sentence(nb_words=10)
    response = await client.post(
        url,
        json={
            "telegram": params,
            "user": {
                "name": name,
                "position": position,
                "about": about,
            },
        },
    )
    json_response = response.json()
    payload = jwt.decode(
        json_response["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    assert response.status_code == status.HTTP_200_OK
    assert params["id"] == payload.get("sub")

    user = await dao.get_user(telegram_id)
    assert user is not None
    assert user.name == name
    assert user.position == position


@pytest.mark.anyio
async def test_get_me(
    fastapi_app: FastAPI,
    client: AsyncClient,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для получения информации о себе."""
    url = fastapi_app.url_path_for("get_me")

    response = await client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = await user_client.get(url)
    json_response = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert json_response["id"] == 2


@pytest.mark.anyio
async def test_update_me(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта для обновления данных о себе."""
    dao = UserDAO()

    new_name = f"{fake.first_name()} {fake.last_name()}"
    new_position = fake.job()

    url = fastapi_app.url_path_for("update_me")
    response = await user_client.put(
        url,
        json={
            "name": new_name,
            "position": new_position,
        },
    )
    updated_user = await dao.get_user(telegram_id=2)

    assert response.status_code == status.HTTP_200_OK
    assert updated_user is not None
    assert updated_user.name == new_name
    assert updated_user.position == new_position
    assert updated_user.about == "user"


@pytest.mark.anyio
async def test_get_user(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест эндпоинта с проверкой существования юзера и правильной работы БД."""
    dao = UserDAO()

    telegram_id = secrets.randbelow(1000000000000)
    await dao.create_user_model(
        telegram_id=telegram_id,
        name=f"{fake.first_name()} {fake.last_name()}",
        position=fake.job(),
        about=fake.sentence(nb_words=10),
    )

    url = fastapi_app.url_path_for("get_user", telegram_id=telegram_id)
    response = await user_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_fail_get_user(
    fastapi_app: FastAPI,
    user_client: AsyncClient,
    fake: Faker,
) -> None:
    """Тест ошибки эндпоинта с проверкой существования юзера и правильной работы БД."""
    url = fastapi_app.url_path_for(
        "get_user",
        telegram_id=secrets.randbelow(1000000000000),
    )
    response = await user_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
