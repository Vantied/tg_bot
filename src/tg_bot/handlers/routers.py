from aiogram import Router

from tg_bot.handlers.bind import bind_router
from tg_bot.handlers.cancel import cancel_router
from tg_bot.handlers.cat import cat_router
from tg_bot.handlers.delete import delete_router
from tg_bot.handlers.errors import errors_router
from tg_bot.handlers.group import group_router
from tg_bot.handlers.help import help_router
from tg_bot.handlers.new import new_router
from tg_bot.handlers.schedule import schedule_router
from tg_bot.handlers.start import start_router
from tg_bot.handlers.template import template_router
from tg_bot.handlers.weather import weather_router

main_router = Router()

main_router.include_router(errors_router)
main_router.include_router(cancel_router)
main_router.include_router(start_router)
main_router.include_router(help_router)
main_router.include_router(cat_router)
main_router.include_router(weather_router)
main_router.include_router(group_router)
main_router.include_router(schedule_router)
main_router.include_router(delete_router)
main_router.include_router(template_router)
# Роутеры с шагами диалогов - последними: их хендлеры состояний
# ловят любой текст, поэтому команды должны проверяться раньше.
main_router.include_router(bind_router)
main_router.include_router(new_router)
