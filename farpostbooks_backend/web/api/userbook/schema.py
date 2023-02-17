from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from farpostbooks_backend.web.api.schema import BookIntroduction


class UserBookModelDTO(BaseModel):
    """DTO для модели истории взятие книг."""

    id: int
    book: int
    user: int
    get_timestamp: datetime
    back_timestamp: datetime
    rating: int


class UserBookIntroduction(BaseModel):
    """DTO для книги пользователя."""

    book: BookIntroduction
    get_timestamp: datetime
    back_timestamp: Optional[datetime]
    rating: Optional[int]

    class Config:
        orm_mode = True


class UserBooks(BaseModel):
    """DTO для спика книг пользователя."""

    current: Optional[UserBookIntroduction]
    books: List[UserBookIntroduction]


class RatingDTO(BaseModel):
    """DTO для рейтинга книги."""

    rating: int
