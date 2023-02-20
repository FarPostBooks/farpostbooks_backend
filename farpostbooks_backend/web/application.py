import logging
from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from tortoise.contrib.fastapi import register_tortoise

from farpostbooks_backend.db.config import TORTOISE_CONFIG
from farpostbooks_backend.services.utils import (
    EndpointFilter,
    PrometheusMiddleware,
    metrics,
    setting_otlp,
)
from farpostbooks_backend.settings import settings
from farpostbooks_backend.web.api.router import api_router
from farpostbooks_backend.web.lifetime import (
    register_shutdown_event,
    register_startup_event,
)


def get_app() -> FastAPI:
    """
    Конструктор для FastAPI приложения.

    :return: Приложение fastapi.
    """
    app = FastAPI(
        title="farpostbooks_backend",
        version=metadata.version("farpostbooks_backend"),
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Ивенты при запуске и выключении.
    register_startup_event(app)
    register_shutdown_event(app)

    # Конфигурация для роутеров.
    app.add_middleware(PrometheusMiddleware, app_name=settings.environment)
    setting_otlp(app, settings.environment, settings.OTLP_GRPC_ENDPOINT)
    app.include_router(router=api_router, prefix="/api")
    app.add_route("/metrics", metrics)
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    # Конфигурация для Tortoise ORM.
    register_tortoise(
        app,
        config=TORTOISE_CONFIG,
        add_exception_handlers=True,
    )

    return app
