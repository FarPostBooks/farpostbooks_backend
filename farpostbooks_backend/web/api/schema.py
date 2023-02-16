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
