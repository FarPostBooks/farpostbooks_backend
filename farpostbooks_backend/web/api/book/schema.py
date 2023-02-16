from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BookModelDTO(BaseModel):
    """DTO для модели книг."""

    id: int
    name: str
    description: str
    image: str
    added_timestamp: datetime

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
