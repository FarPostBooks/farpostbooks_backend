from datetime import datetime

from pydantic import BaseModel


class UserBookModelDTO(BaseModel):
    """DTO для модели истории взятие книг."""

    id: int
    book: int
    user: int
    get_timestamp: datetime
    back_timestamp: datetime
    rating: int
