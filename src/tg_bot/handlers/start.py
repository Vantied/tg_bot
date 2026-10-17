from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

start_router = Router(name=__name__)


@start_router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Отправляет первоначальное сообщение при отправке /start."""
    await message.answer("Hello from my router!")
