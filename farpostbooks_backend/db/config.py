from typing import List

from farpostbooks_backend.settings import settings

MODELS_MODULES: List[str] = [
    "farpostbooks_backend.db.models.userbook_model",
]  # noqa: WPS407

TORTOISE_CONFIG = {  # noqa: WPS407
    "connections": {
        "default": str(settings.db_url),
    },
    "apps": {
        "models": {
            "models": MODELS_MODULES + ["aerich.models"],
            "default_connection": "default",
        },
    },
}
