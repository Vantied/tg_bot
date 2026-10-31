from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, TelegramObject, Update

from tg_bot.core.exceptions import BotValidationError


class ValidationErrorMiddleware(BaseMiddleware):
    """Перехватывает BotValidationError и отвечает пользователю.

    Подключается снаружи GetSessionMiddleware: исключение сначала
    проходит через сессию (транзакция откатывается), и только потом
    пользователь получает сообщение об ошибке.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Вызывает хендлер и превращает ошибку валидации в ответ."""
        try:
            return await handler(event, data)
        except BotValidationError as error:
            await reply(event, error.message)
            return None


async def reply(event: TelegramObject, text: str) -> None:
    """Отвечает в чат, откуда пришло событие (сообщение или кнопка)."""
    if not isinstance(event, Update):
        return
    if event.message is not None:
        await event.message.answer(text)
        return
    callback = event.callback_query
    if callback is None:
        return
    with suppress(TelegramBadRequest):
        await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(text)
