from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> None:
    """
    Проверить работоспособность API.

    Возвращает статус 200, если все в порядке.
    """
