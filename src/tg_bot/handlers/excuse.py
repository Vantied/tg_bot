from aiogram import Bot, Router, html
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from openai import AsyncOpenAI

from tg_bot.core.constants import (
    EXCUSE_BUSY_MESSAGE,
    EXCUSE_MESSAGE,
    EXCUSE_REQUEST_ERROR_MESSAGE,
)
from tg_bot.core.exceptions import BotValidationError
from tg_bot.handlers.validators import (
    check_excuse_cooldown,
    get_llm_client,
    get_user,
    validate_excuse_reason,
)
from tg_bot.services.excuse_api import (
    ExcuseRateLimitError,
    ExcuseRequestError,
    excuse_cooldown,
    generate_excuse,
)

excuse_router = Router(name=__name__)


@excuse_router.message(Command('late'))
async def late_handler(
    message: Message,
    command: CommandObject,
    bot: Bot,
    llm_client: AsyncOpenAI | None,
) -> None:
    """Смешная отмазка за опоздание: /late или /late на пару по матану."""
    client = get_llm_client(llm_client)
    user = get_user(message)
    reason = validate_excuse_reason(command.args)
    check_excuse_cooldown(user.id)
    # Пока нейросеть думает, в чате видно «печатает...».
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        try:
            excuse = await generate_excuse(client, reason)
        except ExcuseRateLimitError as error:
            raise BotValidationError(EXCUSE_BUSY_MESSAGE) from error
        except ExcuseRequestError as error:
            raise BotValidationError(EXCUSE_REQUEST_ERROR_MESSAGE) from error
    excuse_cooldown.mark_used(user.id)
    await message.answer(EXCUSE_MESSAGE.format(excuse=html.quote(excuse)))
