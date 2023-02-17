from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from farpostbooks_backend.web.api.schema import BookIntroduction


class UserBookIntroduction(BaseModel):
    """DTO для книги пользователя."""

    book: BookIntroduction
    get_timestamp: datetime
    back_timestamp: Optional[datetime]
    rating: Optional[int]

    class Config:
        orm_mode = True


class UserBooks(BaseModel):
    """Список книг у пользователя (текущая + прочитанные)."""

    current: Optional[UserBookIntroduction]
    books: List[UserBookIntroduction]


class RatingDTO(BaseModel):
    """Выставление рейтинга книге."""

    rating: int
