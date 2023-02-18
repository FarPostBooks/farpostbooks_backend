from typing import Awaitable, Callable

from fastapi import FastAPI


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Действия при запуске приложения.

    Эта функция использует приложение FastAPI для хранения данных
    в состоянии, например db_engine.

    :param app: Приложение FastAPI.
    :return: Функция, выполняющая действия.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Действия при остановке приложения.

    :param app: Приложение FastAPI.
    :return: Функция, выполняющая действия.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        pass  # noqa: WPS420

    return _shutdown
