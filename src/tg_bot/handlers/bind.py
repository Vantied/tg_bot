import logging
from datetime import UTC, datetime

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.core.constants import (
    ASK_CHAT_ID_MESSAGE,
    CHAT_BOUND_GROUP_MESSAGE,
    CHAT_BOUND_MESSAGE,
    CHAT_TITLE_MAX_LENGTH,
    CHAT_UNBOUND_MESSAGE,
    CHOOSE_CHAT_TO_UNBIND_MESSAGE,
    UNBIND_CALLBACK_PREFIX,
)
from tg_bot.crud.chat import chat_crud
from tg_bot.handlers.filters import IS_PRIVATE
from tg_bot.handlers.keyboards import unbind_keyboard
from tg_bot.handlers.states import BindChat
from tg_bot.handlers.utils import close_keyboard
from tg_bot.handlers.validators import (
    get_admin_group,
    get_bound_chats,
    get_own_bound_chat,
    get_user,
    get_user_schedule,
    validate_chat_id,
)

logger = logging.getLogger(__name__)

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
    await get_user_schedule(session, get_user(message).id)
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
    await bind_chat(message, message.text, bot, state, session)


@bind_router.message(Command('unbind'))
async def unbind_handler(message: Message, session: AsyncSession) -> None:
    """Показывает кнопки с привязанными группами."""
    schedule = await get_user_schedule(session, get_user(message).id)
    chats = await get_bound_chats(session, schedule)
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
    chat = await get_own_bound_chat(
        session,
        callback.data.removeprefix(UNBIND_CALLBACK_PREFIX),
        callback.from_user.id,
    )
    await chat_crud.update(session, chat, {'schedule_id': None})
    await message.answer(
        CHAT_UNBOUND_MESSAGE.format(chat=html.quote(chat.title)),
    )


async def bind_chat(
    message: Message,
    raw_chat_id: str | None,
    bot: Bot,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    """Проверяет группу и права пользователя, затем привязывает."""
    user = get_user(message)
    chat_id = validate_chat_id(raw_chat_id)
    tg_chat = await get_admin_group(bot, chat_id, user.id)
    schedule = await get_user_schedule(session, user.id)

    title = (tg_chat.title or str(chat_id))[:CHAT_TITLE_MAX_LENGTH]
    data = {
        'schedule_id': schedule.id,
        'title': title,
        'bound_by': user.id,
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
        logger.warning('Не удалось написать в группу %s', chat_id)
