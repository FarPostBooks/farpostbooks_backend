from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserModelDTO(BaseModel):
    """DTO для модели пользователей."""

    id: int
    name: str
    position: str
    about: str
    timestamp: datetime

    class Config:
        orm_mode = True


class TelegramUserDTO(BaseModel):
    """DTO для модели данных из Telegram Login Widget'а."""

    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    photo_url: Optional[str]
    auth_date: int
    hash: str


class IsTelegramHashValid(BaseModel):
    """IsTelegramHashValid model."""

    status: bool


class IsUserExist(BaseModel):
    """IsUserExist model."""

    status: bool


class UserModelUpdateDTO(BaseModel):
    """DTO для обновления данных существующего пользователя."""

    name: Optional[str] = Field(None)
    position: Optional[str] = Field(None)
    about: Optional[str] = Field(None)
