from aiogram import Router

from tg_bot.handlers.cancel import cancel_router
from tg_bot.handlers.help import help_router
from tg_bot.handlers.new import new_router
from tg_bot.handlers.start import start_router

main_router = Router()

main_router.include_router(cancel_router)
main_router.include_router(start_router)
main_router.include_router(help_router)
main_router.include_router(new_router)
