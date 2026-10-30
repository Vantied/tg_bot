import logging
from datetime import UTC, datetime

from aiogram import Bot, F, Router, html
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    ASK_CHAT_ID_MESSAGE,
    BAD_CHAT_ID_MESSAGE,
    CHAT_ALREADY_UNBOUND_MESSAGE,
    CHAT_BOUND_GROUP_MESSAGE,
    CHAT_BOUND_MESSAGE,
    CHAT_NOT_FOUND_MESSAGE,
    CHAT_TITLE_MAX_LENGTH,
    CHAT_UNBOUND_MESSAGE,
    CHOOSE_CHAT_TO_UNBIND_MESSAGE,
    NO_BOUND_CHATS_MESSAGE,
    NO_SCHEDULE_PRIVATE_MESSAGE,
    NOT_A_GROUP_MESSAGE,
    NOT_CHAT_ADMIN_MESSAGE,
    UNBIND_CALLBACK_PREFIX,
)
from tg_bot.crud.chat import chat_crud
from tg_bot.crud.schedule import schedule_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.keyboards import unbind_keyboard
from tg_bot.handlers.states import BindChat
from tg_bot.handlers.utils import close_keyboard

logger = logging.getLogger(__name__)

GROUP_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}
ADMIN_STATUSES = {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}

bind_router = Router(name=__name__)
bind_router.message.filter(IS_PRIVATE)


@bind_router.message(Command('bind'))
async def bind_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Привязывает расписание к группе: /bind id или по шагам."""
    if message.from_user is None:
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is None:
        await message.answer(NO_SCHEDULE_PRIVATE_MESSAGE)
        return
    if command.args:
        await bind_chat(message, command.args, bot, state, session)
        return
    await state.set_state(BindChat.chat_id)
    await message.answer(ASK_CHAT_ID_MESSAGE)


@bind_router.message(BindChat.chat_id)
async def chat_id_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Получает id группы на шаге диалога /bind."""
    await bind_chat(message, message.text or '', bot, state, session)


@bind_router.message(Command('unbind'))
async def unbind_handler(message: Message, session: AsyncSession) -> None:
    """Показывает кнопки с привязанными группами."""
    if message.from_user is None:
        return
    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is None:
        await message.answer(NO_SCHEDULE_PRIVATE_MESSAGE)
        return
    chats = await chat_crud.get_by_schedule(session, schedule.id)
    if not chats:
        await message.answer(NO_BOUND_CHATS_MESSAGE)
        return
    await message.answer(
        CHOOSE_CHAT_TO_UNBIND_MESSAGE,
        reply_markup=unbind_keyboard(chats),
    )


@bind_router.callback_query(F.data.startswith(UNBIND_CALLBACK_PREFIX))
async def unbind_chat_handler(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    """Отвязывает выбранную группу от расписания пользователя."""
    message = await close_keyboard(callback)
    if message is None or callback.data is None:
        return
    chat_id = parse_chat_id(callback.data.removeprefix(UNBIND_CALLBACK_PREFIX))
    schedule = await schedule_crud.get_by_owner(session, callback.from_user.id)
    chat = (
        await chat_crud.get(session, chat_id) if chat_id is not None else None
    )
    # Отвязать можно только группу своего расписания.
    if chat is None or schedule is None or chat.schedule_id != schedule.id:
        await message.answer(CHAT_ALREADY_UNBOUND_MESSAGE)
        return
    await chat_crud.update(session, chat, {'schedule_id': None})
    await message.answer(
        CHAT_UNBOUND_MESSAGE.format(chat=html.quote(chat.title))
    )


async def bind_chat(
    message: Message,
    raw_chat_id: str,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Проверяет группу и права пользователя, затем привязывает."""
    if message.from_user is None:
        return
    chat_id = parse_chat_id(raw_chat_id)
    if chat_id is None:
        await message.answer(BAD_CHAT_ID_MESSAGE)
        return
    try:
        tg_chat = await bot.get_chat(chat_id)
        member = await bot.get_chat_member(chat_id, message.from_user.id)
    except (TelegramBadRequest, TelegramForbiddenError):
        # Группы нет, или бота в ней нет - Telegram не отдаёт данные.
        await message.answer(CHAT_NOT_FOUND_MESSAGE)
        return
    if tg_chat.type not in GROUP_TYPES:
        await message.answer(NOT_A_GROUP_MESSAGE)
        return
    if member.status not in ADMIN_STATUSES:
        await message.answer(NOT_CHAT_ADMIN_MESSAGE)
        return

    schedule = await schedule_crud.get_by_owner(session, message.from_user.id)
    if schedule is None:
        await state.clear()
        await message.answer(NO_SCHEDULE_PRIVATE_MESSAGE)
        return
    title = (tg_chat.title or str(chat_id))[:CHAT_TITLE_MAX_LENGTH]
    data = {
        'schedule_id': schedule.id,
        'title': title,
        'bound_by': message.from_user.id,
        'bound_at': datetime.now(UTC),
    }
    chat = await chat_crud.get(session, chat_id)
    if chat is None:
        await chat_crud.create(session, {'id': chat_id, **data})
    else:
        await chat_crud.update(session, chat, data)
    await state.clear()
    await message.answer(
        CHAT_BOUND_MESSAGE.format(
            chat=html.quote(title),
            schedule=html.quote(schedule.title),
        ),
    )
    try:
        await bot.send_message(
            chat_id,
            CHAT_BOUND_GROUP_MESSAGE.format(
                schedule=html.quote(schedule.title),
            ),
        )
    except (TelegramBadRequest, TelegramForbiddenError):
        # Привязка уже сохранена, сообщение в группу - необязательное.
        logger.warning('Не удалось написать в группу %s', chat_id)


def parse_chat_id(raw: str) -> int | None:
    """Id группы - целое число, у групп оно отрицательное."""
    try:
        chat_id = int(raw.strip())
    except ValueError:
        return None
    return chat_id if chat_id < 0 else None
