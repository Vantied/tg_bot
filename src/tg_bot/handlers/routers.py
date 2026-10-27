from aiogram import Router

from tg_bot.handlers.help import help_router
from tg_bot.handlers.start import start_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(help_router)
