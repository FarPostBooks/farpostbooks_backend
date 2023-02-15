from datetime import datetime
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="JWT")


class UserModelDTO(BaseModel):
    """DTO для модели пользователей."""

    id: int
    name: str
    position: str
    about: str
    timestamp: datetime

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    """Данные в JWT токене."""

    id: int


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


class UserModelCreateDTO(BaseModel):
    """Данные для заполнения пользователем при регистрации."""

    name: str
    position: str
    about: str


class CreateUserDTO(BaseModel):
    """Модель для регистрации нового пользователя."""

    telegram: TelegramUserDTO
    user: UserModelCreateDTO


class IsUserExist(BaseModel):
    """IsUserExist model."""

    status: bool


class UserModelUpdateDTO(BaseModel):
    """DTO для обновления данных существующего пользователя."""

    name: Optional[str] = Field(None)
    position: Optional[str] = Field(None)
    about: Optional[str] = Field(None)
