from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tg_bot.core.constants import (
    DELETE_CANCEL_CALLBACK,
    DELETE_CONFIRM_CALLBACK,
    FIRST_WEEK_BUTTON,
    FIRST_WEEK_CALLBACK,
    NO_BUTTON,
    ONE_WEEK_BUTTON,
    ONE_WEEK_CALLBACK,
    SECOND_WEEK_BUTTON,
    SECOND_WEEK_CALLBACK,
    TWO_WEEKS_BUTTON,
    TWO_WEEKS_CALLBACK,
    YES_BUTTON,
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


def yes_or_cancel_keyboard() -> InlineKeyboardMarkup:
    """Кнопки подтверждения удаления: да или отмена."""
    builder = InlineKeyboardBuilder()
    builder.button(text=YES_BUTTON, callback_data=DELETE_CONFIRM_CALLBACK)
    builder.button(text=NO_BUTTON, callback_data=DELETE_CANCEL_CALLBACK)
    builder.adjust(2)
    return builder.as_markup()
