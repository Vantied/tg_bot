from datetime import timedelta

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    CITY_FOR_TIMEZONE_NOT_FOUND_MESSAGE,
    CURRENT_TIMEZONE_MESSAGE,
    TIMEZONE_REQUEST_ERROR_MESSAGE,
    TIMEZONE_SET_MESSAGE,
    WEEK_SWITCHED_MESSAGE,
)
from tg_bot.crud.lesson import lesson_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.validators import (
    find_city_or_error,
    get_chat_schedule,
    get_city_timezone,
    get_current_week,
)
from tg_bot.services.schedule_view import format_day, format_now, format_week
from tg_bot.services.weeks import (
    current_monday,
    local_now,
    local_time_text,
    local_today,
    other_week,
)

schedule_router = Router(name=__name__)


@schedule_router.message(Command('now'))
async def now_handler(message: Message, session: AsyncSession) -> None:
    """Какая пара идёт сейчас и какая следующая."""
    schedule = await get_chat_schedule(message, session)
    lessons = await lesson_crud.get_by_schedule(session, schedule.id)
    await message.answer(
        format_now(schedule, lessons, local_now(schedule.timezone)),
    )


@schedule_router.message(Command('timezone'), IS_PRIVATE)
async def timezone_handler(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    http_session: ClientSession,
) -> None:
    """Показывает или меняет часовой пояс: /timezone Омск."""
    schedule = await get_chat_schedule(message, session)
    if not (command.args or '').strip():
        await message.answer(
            CURRENT_TIMEZONE_MESSAGE.format(
                timezone=schedule.timezone,
                time=local_time_text(schedule.timezone),
            ),
        )
        return
    city = await find_city_or_error(
        http_session,
        command.args.strip(),
        not_found=CITY_FOR_TIMEZONE_NOT_FOUND_MESSAGE,
        request_error=TIMEZONE_REQUEST_ERROR_MESSAGE,
    )
    timezone = get_city_timezone(city)
    await schedule_crud.update(session, schedule, {'timezone': timezone})
    await message.answer(
        TIMEZONE_SET_MESSAGE.format(
            timezone=timezone,
            time=local_time_text(timezone),
        ),
    )


@schedule_router.message(Command('today'))
async def today_handler(message: Message, session: AsyncSession) -> None:
    """Расписание на сегодня."""
    await send_day(message, session, days_ahead=0)


@schedule_router.message(Command('tomorrow'))
async def tomorrow_handler(message: Message, session: AsyncSession) -> None:
    """Расписание на завтра."""
    await send_day(message, session, days_ahead=1)


@schedule_router.message(Command('week'))
async def week_handler(message: Message, session: AsyncSession) -> None:
    """Расписание на текущую неделю."""
    schedule = await get_chat_schedule(message, session)
    lessons = await lesson_crud.get_by_schedule(session, schedule.id)
    await message.answer(
        format_week(schedule, lessons, local_today(schedule.timezone)),
    )


@schedule_router.message(Command('switch_week'), IS_PRIVATE)
async def switch_week_handler(
    message: Message,
    session: AsyncSession,
) -> None:
    """Меняет местами 1-ю и 2-ю неделю, начиная с текущей."""
    schedule = await get_chat_schedule(message, session)
    new_week = other_week(get_current_week(schedule))
    await schedule_crud.update(
        session,
        schedule,
        {
            'anchor_week': new_week,
            'anchor_monday': current_monday(schedule.timezone),
        },
    )
    await message.answer(WEEK_SWITCHED_MESSAGE.format(week=new_week))


async def send_day(
    message: Message,
    session: AsyncSession,
    *,
    days_ahead: int,
) -> None:
    """Отправляет расписание на день: сегодня + days_ahead."""
    schedule = await get_chat_schedule(message, session)
    lessons = await lesson_crud.get_by_schedule(session, schedule.id)
    day = local_today(schedule.timezone) + timedelta(days=days_ahead)
    await message.answer(format_day(schedule, lessons, day) or '')
