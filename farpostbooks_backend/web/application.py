import logging
from importlib import metadata

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
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


def enable_metrics(app: FastAPI) -> None:
    """
    Включение метрик и логирования.

    :param app: Приложение FastAPI.
    """
    app.add_route("/metrics", metrics)
    app.add_middleware(PrometheusMiddleware, app_name=settings.environment)
    setting_otlp(app, settings.environment, settings.OTLP_GRPC_ENDPOINT)
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


def get_app() -> FastAPI:
    """
    Конструктор для FastAPI приложения.

    :return: Приложение FastAPI.
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

    # Конфигурация главного роутера и статики.
    app.mount("/images", StaticFiles(directory="images"), name="images")
    app.include_router(router=api_router, prefix="/api")
    app.router.redirect_slashes = False

    # Метрики и логирование
    enable_metrics(app)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Конфигурация для Tortoise ORM.
    register_tortoise(
        app,
        config=TORTOISE_CONFIG,
        add_exception_handlers=True,
    )

    return app
