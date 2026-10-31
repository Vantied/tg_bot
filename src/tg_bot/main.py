import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.core.constants import BOT_COMMANDS, GROUP_COMMANDS
from tg_bot.core.db import async_engine
from tg_bot.core.settings import settings
from tg_bot.handlers.routers import main_router
from tg_bot.middlewares.db import GetSessionMiddleware
from tg_bot.middlewares.validation import ValidationErrorMiddleware
from tg_bot.services.daily import send_daily_schedules

dp = Dispatcher()
dp.include_router(main_router)
# Порядок важен: middleware, подключённая раньше, - внешняя. Ошибка
# валидации сначала проходит через сессию (откат транзакции), а уже
# потом ValidationErrorMiddleware отвечает пользователю.
dp.update.outer_middleware(ValidationErrorMiddleware())
dp.update.outer_middleware(GetSessionMiddleware())


@dp.startup()
async def on_startup(bot: Bot, dispatcher: Dispatcher) -> None:
    """Меню команд, HTTP-сессия и планировщик рассылки."""
    await bot.set_my_commands(
        [BotCommand(command=c, description=d) for c, d in BOT_COMMANDS],
        scope=BotCommandScopeAllPrivateChats(),
    )
    await bot.set_my_commands(
        [BotCommand(command=c, description=d) for c, d in GROUP_COMMANDS],
        scope=BotCommandScopeAllGroupChats(),
    )
    # Одна HTTP-сессия на всё приложение. Хендлеры получают её
    # параметром http_session.
    dispatcher['http_session'] = ClientSession()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_daily_schedules,
        'cron',
        minute=0,
        kwargs={'bot': bot},
    )
    scheduler.start()
    dispatcher['scheduler'] = scheduler


@dp.shutdown()
async def on_shutdown(dispatcher: Dispatcher) -> None:
    """Аккуратно закрывает всё, что открыли при запуске."""
    dispatcher['scheduler'].shutdown(wait=False)
    await dispatcher['http_session'].close()
    await async_engine.dispose()


async def start_bot() -> None:
    """Запускает бота."""
    bot = Bot(
        token=settings.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await dp.start_polling(bot)


def main() -> None:
    """Запускает главную функцию."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    asyncio.run(start_bot())


if __name__ == '__main__':
    main()
