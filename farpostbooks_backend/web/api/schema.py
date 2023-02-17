from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserModelDTO(BaseModel):
    """Информация о пользователе."""

    id: int
    name: str
    position: str
    about: str
    timestamp: datetime

    class Config:
        orm_mode = True


class UserModelUpdateDTO(BaseModel):
    """Обновление данных пользователя."""

    name: Optional[str] = Field(None)
    position: Optional[str] = Field(None)
    about: Optional[str] = Field(None)


class UserBookModel(BaseModel):
    """Информация о книге, взятой пользователем."""

    user: UserModelDTO
    get_timestamp: datetime
    back_timestamp: Optional[datetime]
    rating: Optional[int]

    class Config:
        orm_mode = True


class BookModelDTO(BaseModel):
    """Подробная информация о книге."""

    id: int
    name: str
    description: str
    image: str
    author: str
    publish: str
    added_timestamp: Optional[datetime]
    user_books: Optional[List[UserBookModel]] = None

    class Config:
        orm_mode = True


class BookIntroduction(BaseModel):
    """Отображение списка книг."""

    id: int
    name: str
    image: str

    class Config:
        orm_mode = True


class ScrollDTO(BaseModel):
    """Параметры для получения списка книг."""

    limit: Optional[int]
    offset: Optional[int]
