from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from farpostbooks_backend.db.models.userbook_model import UserBookModel


class UserModel(models.Model):
    """Модель для таблицы с юзерами."""

    id = fields.BigIntField(pk=True)
    status = fields.CharField(max_length=16, default="user")  # noqa: WPS432
    name = fields.CharField(max_length=64)  # noqa: WPS432
    position = fields.CharField(max_length=64)  # noqa: WPS432
    about = fields.CharField(max_length=255)  # noqa: WPS432
    timestamp = fields.DatetimeField(auto_now_add=True)

    books: fields.ReverseRelation["UserBookModel"]

    def __str__(self) -> str:
        return self.name
