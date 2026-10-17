import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from tg_bot.core.settings import settings
from tg_bot.handlers.routers import main_router
from tg_bot.middlewares.db import GetSessionMiddleware

dp = Dispatcher()
dp.include_router(main_router)
dp.update.outer_middleware(GetSessionMiddleware())


async def start_bot() -> None:
    """Запускает бота."""
    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


def main() -> None:
    """Запускает главную функцию."""
    asyncio.run(start_bot())


if __name__ == '__main__':
    main()
