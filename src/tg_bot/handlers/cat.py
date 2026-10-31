from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import ClientSession

from tg_bot.core.constants import CAT_REQUEST_ERROR_MESSAGE
from tg_bot.core.exceptions import BotValidationError
from tg_bot.services.cat_api import get_random_cat

cat_router = Router(name=__name__)


@cat_router.message(Command('cat'))
async def cat_handler(message: Message, http_session: ClientSession) -> None:
    """Отправляет случайного кота при отправке /cat."""
    cat = await get_random_cat(http_session)
    if cat is None:
        raise BotValidationError(CAT_REQUEST_ERROR_MESSAGE)
    await message.answer_photo(cat)
