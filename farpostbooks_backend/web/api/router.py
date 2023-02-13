from fastapi.routing import APIRouter

from farpostbooks_backend.web.api import monitoring, user

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(user.router, prefix="/user", tags=["user"])
