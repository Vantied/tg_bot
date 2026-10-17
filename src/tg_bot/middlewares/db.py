from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.exc import SQLAlchemyError

from tg_bot.core.exceptions import BadRequestToBD
from tg_bot.core.db import session_maker



class GetSessionMiddleware(BaseMiddleware):
    """Получение асинхронной сессии."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Получает сессию."""
        async with session_maker() as session:
            try:
                data['session'] = session
                result = await handler(event, data)
                await session.commit()
                return result
            except SQLAlchemyError as error:
                await session.rollback()
                raise BadRequestToBD() from error
