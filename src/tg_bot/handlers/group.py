from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tg_bot.core.constants import GROUP_ID_MESSAGE
from tg_bot.handlers.filters import IS_GROUP

group_router = Router(name=__name__)


@group_router.message(Command('group'), IS_GROUP)
async def group_handler(message: Message) -> None:
    """Показывает id группы для /bind."""
    await message.answer(GROUP_ID_MESSAGE.format(chat_id=message.chat.id))
