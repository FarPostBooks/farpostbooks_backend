import enum
from pathlib import Path
from tempfile import gettempdir
from typing import List, Optional

from pydantic import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Возможные уровни логирования."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Настройки приложения.

    Доступ к настройкам можно получить из виртуального окружения.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    origins: List[str] = []
    # Количество воркеров для uvicorn
    workers_count: int = 1
    # Включить перезагрузку uvicorn
    reload: bool = False

    # Текущее окружение
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "farpostbooks_backend"
    db_pass: str = "farpostbooks_backend"
    db_base: str = "farpostbooks_backend"
    db_echo: bool = False

    # Конфигурация OAuth2
    secret_key: str = "secret_key"
    token_type: str = "bearer"
    algorithm: str = "HS256"
    expire_minutes: int = 30

    # Конфигурация для Telegram
    bot_token: str = "42:TOKEN"
    broadcast_sleep: float = 0.05

    # Конфигурация для Google Books
    google_books_url: str = "https://www.googleapis.com/books/v1/volumes"
    google_api_key: Optional[str] = None

    # Метрики
    OTLP_GRPC_ENDPOINT: str = "http://tempo:4317"

    # Настройки Redis'а.
    redis_host: str = "redis"
    redis_port: int = 6379

    @property
    def db_url(self) -> URL:
        """
        Сборка ссылки на основе настроек для доступа к Базе Данных.

        :return: URL базы данных.
        """
        return URL.build(
            scheme="postgres",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "FARPOSTBOOKS_BACKEND_"
        env_file_encoding = "utf-8"


settings = Settings()
