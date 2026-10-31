import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    LESSONS_LOADED_MESSAGE,
    NO_SCHEDULE_FOR_FILE_MESSAGE,
    TEMPLATE_CAPTION,
    TEMPLATE_FILENAME,
)
from tg_bot.crud.lesson import lesson_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.validators import (
    get_user,
    get_user_schedule,
    parse_schedule_file,
    validate_schedule_document,
)
from tg_bot.models import Schedule
from tg_bot.services.excel import build_template

template_router = Router(name=__name__)
template_router.message.filter(IS_PRIVATE)


@template_router.message(Command('template'))
async def template_handler(message: Message, session: AsyncSession) -> None:
    """Присылает шаблон: с текущими занятиями или с примерами."""
    schedule = await schedule_crud.get_by_owner(session, get_user(message).id)
    await send_template(message, session, schedule)


@template_router.message(F.document)
async def schedule_file_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Принимает таблицу и заменяет занятия расписания."""
    if message.document is None:
        return
    document = validate_schedule_document(message.document)
    schedule = await get_user_schedule(
        session,
        get_user(message).id,
        error=NO_SCHEDULE_FOR_FILE_MESSAGE,
    )
    lessons = await parse_schedule_file(
        await bot.download(document),
        is_two_weeks=schedule.is_two_weeks,
    )
    count = await lesson_crud.replace_for_schedule(
        session,
        schedule.id,
        lessons,
    )
    await state.clear()
    await message.answer(LESSONS_LOADED_MESSAGE.format(count=count))


async def send_template(
    message: Message,
    session: AsyncSession,
    schedule: Schedule | None,
) -> None:
    """Отправляет файл шаблона в чат сообщения."""
    lessons = (
        await lesson_crud.get_by_schedule(session, schedule.id)
        if schedule is not None
        else []
    )
    content = await asyncio.to_thread(build_template, lessons)
    await message.answer_document(
        BufferedInputFile(content, filename=TEMPLATE_FILENAME),
        caption=TEMPLATE_CAPTION,
    )
