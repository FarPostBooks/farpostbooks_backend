import secrets
import uuid

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from farpostbooks_backend.db.dao.user_dao import UserDAO


@pytest.mark.anyio
async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Тест эндпоинта с проверкой существования юзера и правильной работы БД."""
    dao = UserDAO()

    telegram_id = secrets.randbelow(1000000000000)
    random_data = uuid.uuid4().hex
    await dao.create_user_model(
        telegram_id=telegram_id,
        name=random_data,
        position=random_data,
        about=random_data,
    )

    url = fastapi_app.url_path_for("check_existing_user")
    response = await client.get(url, params={"telegram_id": telegram_id})
    json_response = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_response["status"]
