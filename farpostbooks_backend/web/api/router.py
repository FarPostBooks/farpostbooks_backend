from fastapi.routing import APIRouter

from farpostbooks_backend.web.api import admin, book, monitoring, user, userbook

api_router = APIRouter(redirect_slashes=False)
api_router.include_router(
    monitoring.router,
)

api_router.include_router(
    userbook.router,
    prefix="/users",
    tags=["Книги пользователей"],
)

api_router.include_router(
    user.router,
    prefix="/users",
    tags=["Пользователи"],
)

api_router.include_router(
    admin.router,
    prefix="/users/{telegram_id}",
    tags=["Администратор"],
)

api_router.include_router(
    book.router,
    prefix="/books",
    tags=["Все книги"],
)
