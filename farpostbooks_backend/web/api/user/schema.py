from typing import Optional

from pydantic import BaseModel


class TelegramUserDTO(BaseModel):
    """DTO для модели данных из Telegram Login Widget'а."""

    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]
    auth_date: int
    hash: str


class AuthorizationToken(BaseModel):
    """Токен для авторизации пользователя."""

    access_token: str
    token_type: str


class UserModelCreateDTO(BaseModel):
    """Данные для заполнения пользователем при регистрации."""

    name: str
    position: str
    about: str


class CreateUserDTO(BaseModel):
    """Модель для регистрации нового пользователя."""

    telegram: TelegramUserDTO
    user: UserModelCreateDTO
