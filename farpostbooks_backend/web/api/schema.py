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


class UserModelUpdateDTO(BaseModel):
    """DTO для обновления данных существующего пользователя."""

    name: Optional[str] = Field(None)
    position: Optional[str] = Field(None)
    about: Optional[str] = Field(None)


class BookModelDTO(BaseModel):
    """DTO для модели книг."""

    id: int
    name: str
    description: str
    image: str
    author: str
    publish: str
    added_timestamp: Optional[datetime]

    class Config:
        orm_mode = True


class BookIntroduction(BaseModel):
    """DTO для отображения книги при скроллинге."""

    id: int
    name: str
    image: str

    class Config:
        orm_mode = True


class ScrollDTO(BaseModel):
    """DTO для скроллинга."""

    limit: Optional[int]
    offset: Optional[int]
