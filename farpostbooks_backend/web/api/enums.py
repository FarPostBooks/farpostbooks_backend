from enum import Enum


class FilterFlag(str, Enum):  # noqa: WPS600
    """Параметр для фильтрации выдачи списка книг."""

    all = "ALL"
    taken = "TAKEN"
    not_taken = "NOT_TAKEN"
