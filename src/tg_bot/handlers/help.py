from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tg_bot.core.constants import GROUP_HELP_MESSAGE, HELP_MESSAGE
from tg_bot.handlers.filters import IS_GROUP, IS_PRIVATE

help_router = Router(name=__name__)


@help_router.message(Command('help'), IS_PRIVATE)
async def help_handler(message: Message) -> None:
    """Отправляет подробную справку в ЛС."""
    await message.answer(HELP_MESSAGE)


@help_router.message(Command('help'), IS_GROUP)
async def help_handler_group(message: Message) -> None:
    """Отправляет справку по командам в группе."""
    await message.answer(GROUP_HELP_MESSAGE)
