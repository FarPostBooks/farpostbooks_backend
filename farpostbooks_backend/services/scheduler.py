import asyncio
import logging
from typing import Any, Dict

from aiogram import Bot, exceptions
from aiogram.enums import ParseMode
from arq import cron
from arq.connections import RedisSettings
from tortoise import Tortoise

from farpostbooks_backend.db.config import TORTOISE_CONFIG
from farpostbooks_backend.db.dao.book_dao import BookDAO
from farpostbooks_backend.db.dao.user_dao import UserDAO
from farpostbooks_backend.settings import settings


async def send_message(
    bot: Bot,
    chat_id: int,
    text: str,
) -> bool:
    """
    Отправка сообщения пользователю в Telegram.

    :param bot: Инстанс бота.
    :param chat_id: ID пользователя, которому будет доставлено сообщение.
    :param text: Текст для отправки.
    :return: Удалось ли отправить сообщение.
    """
    try:
        await bot.send_message(chat_id=chat_id, text=text)
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{chat_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as error:
        logging.error(
            f"Target [ID:{chat_id}]: Flood limit is exceeded."
            f" Sleep {error.retry_after} seconds.",
        )
        await asyncio.sleep(error.retry_after)
        return await send_message(bot, chat_id, text)
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{chat_id}]: failed")
    else:
        logging.info(f"Target [ID:{chat_id}]: success")
        return True
    return False


async def new_books(ctx: Dict[str, Any]) -> None:  # pragma: no cover
    """
    Рассылка в Telegram о добавлении новых книг.

    :param ctx: Данные воркера.
    """
    bot: Bot = ctx["bot"]

    books = await BookDAO().get_new_books()
    books_raw = "<b>📚 Добавлены новые книги:</b>"
    for book in books:
        books_raw = f"{books_raw}\n<b>- {book.name}</b> (ISBN: <code>{book.id}</code>)"

    users = await UserDAO().get_users()
    count = 0
    for user in users:
        if await send_message(bot=bot, chat_id=user.id, text=books_raw):
            count += 1
        await asyncio.sleep(settings.broadcast_sleep)
    logging.info(f"Messages sent: {count}")


async def startup(ctx: Dict[str, Any]) -> None:
    """
    Действия при запуске воркера.

    :param ctx: Данные воркера.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:"  # noqa: WPS323
        "%(lineno)d] - %(message)s",  # noqa: WPS323
    )
    ctx["bot"] = Bot(
        token=settings.bot_token,
        parse_mode=ParseMode.HTML,
    )
    await Tortoise.init(TORTOISE_CONFIG)


class WorkerSettings:
    """Настройки воркера."""

    on_startup = startup
    cron_jobs = [
        cron(
            "farpostbooks_backend.services.scheduler.new_books",
            weekday={0},
            hour=0,
            minute=0,
        ),
    ]
    redis_settings = RedisSettings(settings.redis_host, settings.redis_port)
