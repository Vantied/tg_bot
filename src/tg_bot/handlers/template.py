import asyncio

from aiogram import Bot, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    FILE_EMPTY_MESSAGE,
    FILE_ERRORS_MESSAGE,
    FILE_READ_ERROR_MESSAGE,
    FILE_TOO_BIG_MESSAGE,
    LESSONS_LOADED_MESSAGE,
    MAX_SCHEDULE_FILE_SIZE,
    MAX_SHOWN_FILE_ERRORS,
    MORE_FILE_ERRORS,
    NO_SCHEDULE_FOR_FILE_MESSAGE,
    NOT_XLSX_MESSAGE,
    TEMPLATE_CAPTION,
    TEMPLATE_FILENAME,
)
from tg_bot.core.exceptions import ScheduleFileReadError
from tg_bot.crud.lesson import lesson_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.models import Schedule
from tg_bot.services.excel import build_template, parse_schedule

template_router = Router(name=__name__)
template_router.message.filter(IS_PRIVATE)


@template_router.message(Command('template'))
async def template_handler(message: Message, session: AsyncSession) -> None:
    """Присылает шаблон: с текущими занятиями или с примерами."""
    if message.from_user is None:
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    await send_template(message, session, schedule)


@template_router.message(F.document)
async def schedule_file_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Принимает таблицу и заменяет занятия расписания."""
    document = message.document
    if document is None or message.from_user is None:
        return
    if not (document.file_name or '').lower().endswith('.xlsx'):
        await message.answer(NOT_XLSX_MESSAGE)
        return
    if (document.file_size or 0) > MAX_SCHEDULE_FILE_SIZE:
        await message.answer(FILE_TOO_BIG_MESSAGE)
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is None:
        await message.answer(NO_SCHEDULE_FOR_FILE_MESSAGE)
        return

    file = await bot.download(document)
    if file is None:
        await message.answer(FILE_READ_ERROR_MESSAGE)
        return
    try:
        lessons, errors = await asyncio.to_thread(
            parse_schedule,
            file,
            is_two_weeks=schedule.is_two_weeks,
        )
    except ScheduleFileReadError:
        await message.answer(FILE_READ_ERROR_MESSAGE)
        return

    if errors:
        await message.answer(
            FILE_ERRORS_MESSAGE.format(errors=format_errors(errors)),
        )
        return
    if not lessons:
        await message.answer(FILE_EMPTY_MESSAGE)
        return
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


def format_errors(errors: list[str]) -> str:
    """Готовит список ошибок для сообщения: экранирует и обрезает."""
    shown = [html.quote(error) for error in errors[:MAX_SHOWN_FILE_ERRORS]]
    hidden = len(errors) - len(shown)
    if hidden:
        shown.append(MORE_FILE_ERRORS.format(count=hidden))
    return '\n'.join(shown)
