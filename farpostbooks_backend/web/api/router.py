from fastapi.routing import APIRouter

from farpostbooks_backend.web.api import book, monitoring, user

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(book.router, prefix="/books", tags=["books"])
