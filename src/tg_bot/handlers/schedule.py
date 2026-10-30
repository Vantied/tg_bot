from datetime import timedelta

from aiogram import Router, html
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    CITY_FOR_TIMEZONE_NOT_FOUND_MESSAGE,
    CURRENT_TIMEZONE_MESSAGE,
    NO_SCHEDULE_GROUP_MESSAGE,
    NO_SCHEDULE_PRIVATE_MESSAGE,
    NOT_TWO_WEEKS_MESSAGE,
    TIMEZONE_REQUEST_ERROR_MESSAGE,
    TIMEZONE_SET_MESSAGE,
    WEEK_SWITCHED_MESSAGE,
)
from tg_bot.crud.chat import chat_crud
from tg_bot.crud.lesson import lesson_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.models import Schedule
from tg_bot.services.schedule_view import format_day, format_now, format_week
from tg_bot.services.weather_api import WeatherRequestError, find_city
from tg_bot.services.weeks import (
    current_monday,
    local_now,
    local_time_text,
    local_today,
    other_week,
    week_number,
)

schedule_router = Router(name=__name__)


@schedule_router.message(Command('now'))
async def now_handler(message: Message, session: AsyncSession) -> None:
    """Какая пара идёт сейчас и какая следующая."""
    schedule = await find_schedule(message, session)
    if schedule is None:
        return
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
    schedule = await find_schedule(message, session)
    if schedule is None:
        return
    query = (command.args or '').strip()
    if not query:
        await message.answer(
            CURRENT_TIMEZONE_MESSAGE.format(
                timezone=schedule.timezone,
                time=local_time_text(schedule.timezone),
            ),
        )
        return
    try:
        city = await find_city(http_session, query)
    except WeatherRequestError:
        await message.answer(TIMEZONE_REQUEST_ERROR_MESSAGE)
        return
    if city is None:
        await message.answer(
            CITY_FOR_TIMEZONE_NOT_FOUND_MESSAGE.format(city=html.quote(query)),
        )
        return
    if city.timezone is None:
        await message.answer(TIMEZONE_REQUEST_ERROR_MESSAGE)
        return
    await schedule_crud.update(session, schedule, {'timezone': city.timezone})
    await message.answer(
        TIMEZONE_SET_MESSAGE.format(
            timezone=city.timezone,
            time=local_time_text(city.timezone),
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
    schedule = await find_schedule(message, session)
    if schedule is None:
        return
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
    schedule = await find_schedule(message, session)
    if schedule is None:
        return
    current = week_number(schedule, local_today(schedule.timezone))
    if current is None:
        await message.answer(NOT_TWO_WEEKS_MESSAGE)
        return
    new_week = other_week(current)
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
    schedule = await find_schedule(message, session)
    if schedule is None:
        return
    lessons = await lesson_crud.get_by_schedule(session, schedule.id)
    day = local_today(schedule.timezone) + timedelta(days=days_ahead)
    await message.answer(format_day(schedule, lessons, day) or '')


async def find_schedule(
    message: Message,
    session: AsyncSession,
) -> Schedule | None:
    """Расписание для чата: своё в личке, привязанное - в группе.

    Если расписания нет, сам отвечает пользователю и возвращает None.
    """
    if message.chat.type == ChatType.PRIVATE:
        schedule = (
            await schedule_crud.get_by_owner(session, message.from_user.id)
            if message.from_user
            else None
        )
        if schedule is None:
            await message.answer(NO_SCHEDULE_PRIVATE_MESSAGE)
        return schedule

    chat = await chat_crud.get(session, message.chat.id)
    schedule = (
        await schedule_crud.get(session, chat.schedule_id)
        if chat is not None and chat.schedule_id is not None
        else None
    )
    if schedule is None:
        await message.answer(NO_SCHEDULE_GROUP_MESSAGE)
    return schedule
