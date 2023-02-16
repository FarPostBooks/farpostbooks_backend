from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, root_validator


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


class CreateBookModelDTO(BookModelDTO):
    """DTO для добавления книги в базу данных."""

    @classmethod
    @root_validator()
    def rename_fields_for_db(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Переименование книги.

        :param values: Значения исходной модели.
        :return: Словарь с переименованными ключами.
        """
        if "id" in values:
            values["book_id"] = values.get("id")
            values.pop("id")
        return values


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
