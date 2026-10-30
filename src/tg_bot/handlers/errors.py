import logging

from aiogram import Router
from aiogram.types import ErrorEvent

from tg_bot.core.constants import UNEXPECTED_ERROR_MESSAGE

logger = logging.getLogger(__name__)

errors_router = Router(name=__name__)


@errors_router.errors()
async def errors_handler(event: ErrorEvent) -> None:
    """Пишет ошибку в лог и вежливо отвечает пользователю."""
    logger.exception(
        'Ошибка при обработке update %s',
        event.update.update_id,
        exc_info=event.exception,
    )
    message = event.update.message or (
        event.update.callback_query.message
        if event.update.callback_query
        else None
    )
    if message is None:
        return
    try:
        await message.answer(UNEXPECTED_ERROR_MESSAGE)
    except Exception:
        # Если не получилось даже ответить - ошибка уже в логе.
        logger.exception('Не удалось отправить сообщение об ошибке')
