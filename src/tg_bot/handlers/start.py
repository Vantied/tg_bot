from aiogram import Router, html
from aiogram.filters import (
    CommandStart,
    JOIN_TRANSITION,
    ChatMemberUpdatedFilter,
)
from aiogram.types import (
    Message,
    ChatMemberUpdated,
)

from tg_bot.core.constants import (
    START_MESSAGE,
    UNKNOWN_USER,
    GROUP_START_MESSAGE,
)
from tg_bot.handlers.filters import IS_GROUP, IS_PRIVATE

start_router = Router(name=__name__)


@start_router.message(CommandStart(), IS_PRIVATE)
async def start_handler(message: Message) -> None:
    """Отправляет первоначальное сообщение при отправке /start в ЛС."""
    full_name = (
        message.from_user.full_name if message.from_user else UNKNOWN_USER
    )
    await message.answer(START_MESSAGE.format(name=html.quote(full_name)))


@start_router.message(CommandStart(), IS_GROUP)
async def start_handler_group(message: Message) -> None:
    """Отправляет первоначальное сообщение при отправке /start в Группе."""
    await message.answer(GROUP_START_MESSAGE.format(chat_id=message.chat.id))


@start_router.my_chat_member(
    ChatMemberUpdatedFilter(JOIN_TRANSITION), IS_GROUP
)
async def start_handler_join(event: ChatMemberUpdated) -> None:
    """Отправляет первоначальное сообщение.

    При добавлении бота в группу.
    """
    await event.answer(GROUP_START_MESSAGE.format(chat_id=event.chat.id))
