from aiogram.types import CallbackQuery, Message


async def close_keyboard(callback: CallbackQuery) -> Message | None:
    """Отвечает на нажатие и убирает кнопки, чтобы не нажали дважды."""
    await callback.answer()
    if not isinstance(callback.message, Message):
        return None
    await callback.message.edit_reply_markup(reply_markup=None)
    return callback.message
