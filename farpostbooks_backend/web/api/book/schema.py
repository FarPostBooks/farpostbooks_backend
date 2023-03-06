from typing import Optional

from farpostbooks_backend.web.api.enums import FilterFlag
from farpostbooks_backend.web.api.schema import ScrollDTO


class BooksDTO(ScrollDTO):
    """Получение списка книг с учетом фильтров."""

    flag: Optional[FilterFlag] = FilterFlag.all
