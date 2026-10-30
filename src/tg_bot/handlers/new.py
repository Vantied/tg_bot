from datetime import date

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    ASK_CURRENT_WEEK_MESSAGE,
    ASK_LENGTH_MESSAGE,
    ASK_TITLE_MESSAGE,
    DEFAULT_TIMEZONE,
    FIRST_WEEK,
    FIRST_WEEK_CALLBACK,
    ONE_WEEK_CALLBACK,
    PRESS_BUTTON_MESSAGE,
    SCHEDULE_CREATED_MESSAGE,
    SCHEDULE_EXISTS_MESSAGE,
    SCHEDULE_TITLE_MAX_LENGTH,
    SECOND_WEEK,
    SECOND_WEEK_CALLBACK,
    TITLE_NOT_TEXT_MESSAGE,
    TITLE_TOO_LONG_MESSAGE,
    TWO_WEEKS_CALLBACK,
)
from tg_bot.crud.schedule import schedule_crud
from tg_bot.crud.user import user_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.keyboards import (
    current_week_keyboard,
    schedule_length_keyboard,
)
from tg_bot.handlers.states import NewSchedule
from tg_bot.handlers.validators import validate_user_exist
from tg_bot.services.weeks import current_monday

new_router = Router(name=__name__)
new_router.message.filter(IS_PRIVATE)


@new_router.message(Command('new'))
async def new_handler(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Начинает создание расписания, если его ещё нет."""
    if message.from_user is None:
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is not None:
        await message.answer(
            SCHEDULE_EXISTS_MESSAGE.format(title=html.quote(schedule.title)),
        )
        return
    await state.set_state(NewSchedule.title)
    await message.answer(ASK_TITLE_MESSAGE)


@new_router.message(NewSchedule.title)
async def title_handler(message: Message, state: FSMContext) -> None:
    """Сохраняет название и спрашивает длину расписания."""
    title = (message.text or '').strip()
    if not title:
        await message.answer(TITLE_NOT_TEXT_MESSAGE)
        return
    if len(title) > SCHEDULE_TITLE_MAX_LENGTH:
        await message.answer(TITLE_TOO_LONG_MESSAGE)
        return
    await state.update_data(title=title)
    await state.set_state(NewSchedule.two_weeks)
    await message.answer(
        ASK_LENGTH_MESSAGE,
        reply_markup=schedule_length_keyboard(),
    )


@new_router.message(NewSchedule.two_weeks)
@new_router.message(NewSchedule.current_week)
async def press_button_handler(message: Message) -> None:
    """Напоминает, что на этих шагах нужно нажать кнопку."""
    await message.answer(PRESS_BUTTON_MESSAGE)


@new_router.callback_query(NewSchedule.two_weeks, F.data == ONE_WEEK_CALLBACK)
async def one_week_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Расписание на 7 дней: вопрос о текущей неделе не нужен."""
    message = await close_keyboard(callback)
    if message is None:
        return
    await create_schedule(
        callback,
        message,
        state,
        session,
        is_two_weeks=False,
        anchor_week=None,
        anchor_monday=None,
    )


@new_router.callback_query(
    NewSchedule.two_weeks,
    F.data == TWO_WEEKS_CALLBACK,
)
async def two_weeks_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Расписание на 14 дней: спрашивает, какая неделя сейчас."""
    message = await close_keyboard(callback)
    if message is None:
        return
    await state.set_state(NewSchedule.current_week)
    await message.answer(
        ASK_CURRENT_WEEK_MESSAGE,
        reply_markup=current_week_keyboard(),
    )


@new_router.callback_query(
    NewSchedule.current_week,
    F.data.in_({FIRST_WEEK_CALLBACK, SECOND_WEEK_CALLBACK}),
)
async def current_week_handler(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Запоминает текущую неделю и создаёт расписание."""
    message = await close_keyboard(callback)
    if message is None:
        return
    anchor_week = (
        FIRST_WEEK if callback.data == FIRST_WEEK_CALLBACK else SECOND_WEEK
    )
    await create_schedule(
        callback,
        message,
        state,
        session,
        is_two_weeks=True,
        anchor_week=anchor_week,
        anchor_monday=current_monday(DEFAULT_TIMEZONE),
    )


async def close_keyboard(callback: CallbackQuery) -> Message | None:
    """Отвечает на нажатие и убирает кнопки, чтобы не нажали дважды."""
    await callback.answer()
    if not isinstance(callback.message, Message):
        return None
    await callback.message.edit_reply_markup(reply_markup=None)
    return callback.message


async def create_schedule(
    callback: CallbackQuery,
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    *,
    is_two_weeks: bool,
    anchor_week: int | None,
    anchor_monday: date | None,
) -> None:
    """Сохраняет пользователя и расписание, затем ждёт файл."""
    user = callback.from_user
    if not await validate_user_exist(session, user.id):
        await user_crud.create(
            session,
            {'id': user.id, 'full_name': user.full_name},
        )
    data = await state.get_data()
    schedule = await schedule_crud.create(
        session,
        {
            'owner_id': user.id,
            'title': data['title'],
            'is_two_weeks': is_two_weeks,
            'anchor_week': anchor_week,
            'anchor_monday': anchor_monday,
        },
    )
    await state.set_state(NewSchedule.waiting_file)
    await message.answer(
        SCHEDULE_CREATED_MESSAGE.format(title=html.quote(schedule.title)),
    )
