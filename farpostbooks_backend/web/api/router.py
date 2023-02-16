from fastapi.routing import APIRouter

from farpostbooks_backend.web.api import admin, book, monitoring, user

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/users/{telegram_id}", tags=["admin"])
api_router.include_router(book.router, prefix="/books", tags=["books"])
