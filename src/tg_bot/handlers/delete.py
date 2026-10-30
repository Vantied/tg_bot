from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    DELETE_CANCEL_CALLBACK,
    DELETE_CANCELLED_MESSAGE,
    DELETE_CONFIRM_CALLBACK,
    DELETE_CONFIRM_MESSAGE,
    NOTHING_TO_DELETE_MESSAGE,
    SCHEDULE_DELETED_MESSAGE,
)
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.keyboards import yes_or_cancel_keyboard
from tg_bot.handlers.utils import close_keyboard

delete_router = Router(name=__name__)


@delete_router.message(Command('delete'), IS_PRIVATE)
async def delete_handler(message: Message, session: AsyncSession) -> None:
    """Спрашивает подтверждение на удаление расписания."""
    if message.from_user is None:
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is None:
        await message.answer(NOTHING_TO_DELETE_MESSAGE)
        return
    await message.answer(
        DELETE_CONFIRM_MESSAGE.format(title=html.quote(schedule.title)),
        reply_markup=yes_or_cancel_keyboard(),
    )


@delete_router.callback_query(F.data == DELETE_CONFIRM_CALLBACK)
async def delete_confirm_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Удаляет расписание после подтверждения."""
    message = await close_keyboard(callback)
    if message is None:
        return
    schedule = await schedule_crud.get_by_owner(session, callback.from_user.id)
    if schedule is None:
        await message.answer(NOTHING_TO_DELETE_MESSAGE)
        return
    title = schedule.title
    await schedule_crud.remove(session, schedule)
    await state.clear()
    await message.answer(
        SCHEDULE_DELETED_MESSAGE.format(title=html.quote(title))
    )


@delete_router.callback_query(F.data == DELETE_CANCEL_CALLBACK)
async def delete_cancel_handler(callback: CallbackQuery) -> None:
    """Отменяет удаление."""
    message = await close_keyboard(callback)
    if message is None:
        return
    await message.answer(DELETE_CANCELLED_MESSAGE)
