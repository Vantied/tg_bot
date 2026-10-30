from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tg_bot.core.constants import (
    FIRST_WEEK_BUTTON,
    FIRST_WEEK_CALLBACK,
    ONE_WEEK_BUTTON,
    ONE_WEEK_CALLBACK,
    SECOND_WEEK_BUTTON,
    SECOND_WEEK_CALLBACK,
    TWO_WEEKS_BUTTON,
    TWO_WEEKS_CALLBACK,
)


def schedule_length_keyboard() -> InlineKeyboardMarkup:
    """Кнопки выбора длины расписания: 7 или 14 дней."""
    builder = InlineKeyboardBuilder()
    builder.button(text=ONE_WEEK_BUTTON, callback_data=ONE_WEEK_CALLBACK)
    builder.button(text=TWO_WEEKS_BUTTON, callback_data=TWO_WEEKS_CALLBACK)
    builder.adjust(1)
    return builder.as_markup()


def current_week_keyboard() -> InlineKeyboardMarkup:
    """Кнопки выбора текущей недели: 1-я или 2-я."""
    builder = InlineKeyboardBuilder()
    builder.button(text=FIRST_WEEK_BUTTON, callback_data=FIRST_WEEK_CALLBACK)
    builder.button(
        text=SECOND_WEEK_BUTTON,
        callback_data=SECOND_WEEK_CALLBACK,
    )
    builder.adjust(2)
    return builder.as_markup()
