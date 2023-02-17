import hashlib
import hmac
from typing import Any, Dict, Union

from farpostbooks_backend.settings import settings


class HashCheck:
    """Класс для проверки Telegram Hash'а."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Инициализация и добавление данных.

        :param data: Данные от Telegram Login Widget'а.
        """
        if "hash" in data:
            self.hash: str = data.pop("hash")
        self.api_token: str = settings.bot_token
        self.secret_key: bytes = hashlib.sha256(self.api_token.encode()).digest()
        self.data: Dict[str, Union[str, int]] = data

    def data_check_string(self) -> str:
        """
        Преобразование данных, требуемых для генерации hash'а.

        :return: Преобразованные данные.
        """
        sorted_data = sorted(self.data.items())
        data_string = [f"{data[0]}={data[1]}" for data in sorted_data]  # noqa: WPS221
        return "\n".join(data_string)

    def calc_hash(self) -> str:
        """Генерация hash'а на основе полученных данных.

        :return: Telegram Hash.
        """
        msg = bytearray(self.data_check_string(), "utf-8")
        return hmac.new(self.secret_key, msg=msg, digestmod=hashlib.sha256).hexdigest()

    def check_hash(self) -> bool:
        """
        Проверка валидности hash'а.

        :return: Валиден ли Hash - True/False.
        """
        return self.hash == self.calc_hash()
