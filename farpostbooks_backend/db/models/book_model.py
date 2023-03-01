from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from farpostbooks_backend.db.models.userbook_model import UserBookModel


class BookModel(models.Model):
    """Модель для таблицы с книгами."""

    id = fields.BigIntField(pk=True)
    name = fields.CharField(max_length=128)  # noqa: WPS432
    description = fields.TextField()  # noqa: WPS432
    image = fields.CharField(max_length=64)  # noqa: WPS432
    author = fields.CharField(max_length=255)  # noqa: WPS432
    publish = fields.CharField(max_length=16)  # noqa: WPS432
    added_timestamp = fields.DatetimeField(auto_now_add=True)

    user_books: fields.ReverseRelation["UserBookModel"]  # noqa: F821

    def __str__(self) -> str:
        return self.name
