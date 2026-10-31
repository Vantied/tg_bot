from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.core.constants import CANCEL_MESSAGE, NOTHING_TO_CANCEL_MESSAGE
from tg_bot.core.exceptions import BotValidationError

cancel_router = Router(name=__name__)


@cancel_router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Сбрасывает текущий диалог, если он есть."""
    if await state.get_state() is None:
        raise BotValidationError(NOTHING_TO_CANCEL_MESSAGE)
    await state.clear()
    await message.answer(CANCEL_MESSAGE)
