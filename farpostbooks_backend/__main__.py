import logging

import uvicorn

from farpostbooks_backend.services.utils import EndpointFilter
from farpostbooks_backend.settings import settings


def main() -> None:
    """Точка запуска приложения."""
    # Конфигурация для логгирования
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = (
        "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:"  # noqa: WPS323
        "%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s "  # noqa: WPS323
        "resource.service.name=%(otelServiceName)s] - %(message)s"  # noqa: WPS323
    )
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    # Запуск uvicorn
    uvicorn.run(
        "farpostbooks_backend.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=log_config,
        log_level=settings.log_level.value.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()
