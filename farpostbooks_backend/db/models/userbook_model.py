from tortoise import fields, models

from farpostbooks_backend.db.models.book_model import BookModel
from farpostbooks_backend.db.models.user_model import UserModel


class UserBookModel(models.Model):
    """Модель для таблицы с книгами, которые были у юзеров."""

    id = fields.BigIntField(pk=True)
    user: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        model_name="models.UserModel",
        related_name="books",
        on_delete="CASCADE",
    )
    book: fields.ForeignKeyRelation[BookModel] = fields.ForeignKeyField(
        model_name="models.BookModel",
        related_name="user_books",
        on_delete="CASCADE",
    )
    get_timestamp = fields.DatetimeField(auto_now_add=True)
    back_timestamp = fields.DatetimeField(null=True)
    rating = fields.SmallIntField()

    def __str__(self) -> str:
        return str(self.id)
