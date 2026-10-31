import asyncio
from collections.abc import Sequence
from typing import Any, BinaryIO

from aiogram import Bot, html
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import CallbackQuery, ChatFullInfo, Document, Message, User
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    BAD_CHAT_ID_MESSAGE,
    CHAT_ALREADY_UNBOUND_MESSAGE,
    CHAT_NOT_FOUND_MESSAGE,
    FILE_EMPTY_MESSAGE,
    FILE_ERRORS_MESSAGE,
    FILE_READ_ERROR_MESSAGE,
    FILE_TOO_BIG_MESSAGE,
    MAX_SCHEDULE_FILE_SIZE,
    MAX_SHOWN_FILE_ERRORS,
    MORE_FILE_ERRORS,
    NO_BOUND_CHATS_MESSAGE,
    NO_SCHEDULE_GROUP_MESSAGE,
    NO_SCHEDULE_PRIVATE_MESSAGE,
    NOT_A_GROUP_MESSAGE,
    NOT_CHAT_ADMIN_MESSAGE,
    NOT_TWO_WEEKS_MESSAGE,
    NOT_XLSX_MESSAGE,
    SCHEDULE_EXISTS_MESSAGE,
    SCHEDULE_TITLE_MAX_LENGTH,
    TIMEZONE_REQUEST_ERROR_MESSAGE,
    TITLE_NOT_TEXT_MESSAGE,
    TITLE_TOO_LONG_MESSAGE,
    USER_NOT_DEFINED_MESSAGE,
)
from tg_bot.core.exceptions import BotValidationError, ScheduleFileReadError
from tg_bot.crud.chat import chat_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.crud.user import user_crud
from tg_bot.models import Chat, Schedule
from tg_bot.services.excel import parse_schedule
from tg_bot.services.weather_api import City, WeatherRequestError, find_city
from tg_bot.services.weeks import local_today, week_number

GROUP_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}
ADMIN_STATUSES = {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}


# --- Пользователь ---


async def validate_user_exist(session: AsyncSession, user_id: int) -> bool:
    """Проверяет существует ли пользователь."""
    user = await user_crud.get(session, user_id)
    return user is not None


def get_user(event: Message | CallbackQuery) -> User:
    """Автор сообщения или нажатия кнопки."""
    if event.from_user is None:
        raise BotValidationError(USER_NOT_DEFINED_MESSAGE)
    return event.from_user


# --- Расписание ---


async def get_user_schedule(
    session: AsyncSession,
    user_id: int,
    *,
    error: str = NO_SCHEDULE_PRIVATE_MESSAGE,
) -> Schedule:
    """Расписание пользователя. Нет расписания - ошибка с текстом error."""
    schedule = await schedule_crud.get_by_owner(session, user_id)
    if schedule is None:
        raise BotValidationError(error)
    return schedule


async def check_schedule_not_exists(
    session: AsyncSession,
    user_id: int,
) -> None:
    """Одно расписание на пользователя: второе создать нельзя."""
    schedule = await schedule_crud.get_by_owner(session, user_id)
    if schedule is not None:
        raise BotValidationError(
            SCHEDULE_EXISTS_MESSAGE.format(title=html.quote(schedule.title)),
        )


async def get_chat_schedule(
    message: Message,
    session: AsyncSession,
) -> Schedule:
    """Своё расписание в личке, привязанное - в группе."""
    if message.chat.type == ChatType.PRIVATE:
        return await get_user_schedule(session, get_user(message).id)
    chat = await chat_crud.get(session, message.chat.id)
    schedule = (
        await schedule_crud.get(session, chat.schedule_id)
        if chat is not None and chat.schedule_id is not None
        else None
    )
    if schedule is None:
        raise BotValidationError(NO_SCHEDULE_GROUP_MESSAGE)
    return schedule


def get_current_week(schedule: Schedule) -> int:
    """Текущая неделя (1 или 2). Для расписания на 7 дней - ошибка."""
    current = week_number(schedule, local_today(schedule.timezone))
    if current is None:
        raise BotValidationError(NOT_TWO_WEEKS_MESSAGE)
    return current


def validate_title(text: str | None) -> str:
    """Название: текст, не пустой, не длиннее лимита."""
    title = (text or '').strip()
    if not title:
        raise BotValidationError(TITLE_NOT_TEXT_MESSAGE)
    if len(title) > SCHEDULE_TITLE_MAX_LENGTH:
        raise BotValidationError(TITLE_TOO_LONG_MESSAGE)
    return title


# --- Город и часовой пояс ---


def validate_city_query(text: str | None, *, empty_error: str) -> str:
    """Название города не пустое."""
    query = (text or '').strip()
    if not query:
        raise BotValidationError(empty_error)
    return query


async def find_city_or_error(
    http_session: ClientSession,
    query: str,
    *,
    not_found: str,
    request_error: str,
) -> City:
    """Ищет город. Не найден или сервис недоступен - ошибка.

    not_found - шаблон с {city}.
    """
    try:
        city = await find_city(http_session, query)
    except WeatherRequestError as error:
        raise BotValidationError(request_error) from error
    if city is None:
        raise BotValidationError(not_found.format(city=html.quote(query)))
    return city


def get_city_timezone(city: City) -> str:
    """Часовой пояс города. Сервис его не прислал - ошибка."""
    if city.timezone is None:
        raise BotValidationError(TIMEZONE_REQUEST_ERROR_MESSAGE)
    return city.timezone


# --- Группы ---


def validate_chat_id(raw: str | None) -> int:
    """Id группы - целое отрицательное число."""
    try:
        chat_id = int((raw or '').strip())
    except ValueError:
        chat_id = 0
    if chat_id >= 0:
        raise BotValidationError(BAD_CHAT_ID_MESSAGE)
    return chat_id


async def get_admin_group(
    bot: Bot, chat_id: int, user_id: int
) -> ChatFullInfo:
    """Группа существует, бот в ней, а пользователь - её администратор."""
    try:
        tg_chat = await bot.get_chat(chat_id)
        member = await bot.get_chat_member(chat_id, user_id)
    except (TelegramBadRequest, TelegramForbiddenError) as error:
        raise BotValidationError(CHAT_NOT_FOUND_MESSAGE) from error
    if tg_chat.type not in GROUP_TYPES:
        raise BotValidationError(NOT_A_GROUP_MESSAGE)
    if member.status not in ADMIN_STATUSES:
        raise BotValidationError(NOT_CHAT_ADMIN_MESSAGE)
    return tg_chat


async def get_bound_chats(
    session: AsyncSession,
    schedule: Schedule,
) -> Sequence[Chat]:
    """Группы, привязанные к расписанию. Нет ни одной - ошибка."""
    chats = await chat_crud.get_by_schedule(session, schedule.id)
    if not chats:
        raise BotValidationError(NO_BOUND_CHATS_MESSAGE)
    return chats


async def get_own_bound_chat(
    session: AsyncSession,
    raw_chat_id: str,
    user_id: int,
) -> Chat:
    """Группа, привязанная именно к расписанию этого пользователя."""
    try:
        chat_id = validate_chat_id(raw_chat_id)
    except BotValidationError as error:
        raise BotValidationError(CHAT_ALREADY_UNBOUND_MESSAGE) from error
    schedule = await schedule_crud.get_by_owner(session, user_id)
    chat = await chat_crud.get(session, chat_id)
    if chat is None or schedule is None or chat.schedule_id != schedule.id:
        raise BotValidationError(CHAT_ALREADY_UNBOUND_MESSAGE)
    return chat


# --- Файл расписания ---


def validate_schedule_document(document: Document) -> Document:
    """Файл .xlsx и не больше лимита."""
    if not (document.file_name or '').lower().endswith('.xlsx'):
        raise BotValidationError(NOT_XLSX_MESSAGE)
    if (document.file_size or 0) > MAX_SCHEDULE_FILE_SIZE:
        raise BotValidationError(FILE_TOO_BIG_MESSAGE)
    return document


async def parse_schedule_file(
    file: BinaryIO | None,
    *,
    is_two_weeks: bool,
) -> list[dict[str, Any]]:
    """Разбирает таблицу. Любая проблема с файлом - ошибка с пояснением."""
    if file is None:
        raise BotValidationError(FILE_READ_ERROR_MESSAGE)
    try:
        lessons, errors = await asyncio.to_thread(
            parse_schedule,
            file,
            is_two_weeks=is_two_weeks,
        )
    except ScheduleFileReadError as error:
        raise BotValidationError(FILE_READ_ERROR_MESSAGE) from error
    if errors:
        raise BotValidationError(
            FILE_ERRORS_MESSAGE.format(errors=format_errors(errors)),
        )
    if not lessons:
        raise BotValidationError(FILE_EMPTY_MESSAGE)
    return lessons


def format_errors(errors: list[str]) -> str:
    """Готовит список ошибок для сообщения: экранирует и обрезает."""
    shown = [html.quote(error) for error in errors[:MAX_SHOWN_FILE_ERRORS]]
    hidden = len(errors) - len(shown)
    if hidden:
        shown.append(MORE_FILE_ERRORS.format(count=hidden))
    return '\n'.join(shown)
