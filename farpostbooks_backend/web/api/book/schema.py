from datetime import datetime

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
