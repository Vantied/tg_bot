import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from tg_bot.core.constants import DAILY_SCHEDULE_HEADER, DAILY_SCHEDULE_HOUR
from tg_bot.core.db import session_maker
from tg_bot.crud.chat import chat_crud
from tg_bot.services.schedule_view import format_day

logger = logging.getLogger(__name__)


async def send_daily_schedules(bot: Bot) -> None:
    """Рассылает расписание на сегодня в привязанные группы.

    Запускается раз в час. Отправляет только тем группам, у чьего
    расписания сейчас DAILY_SCHEDULE_HOUR по его часовому поясу,
    и только если сегодня есть занятия.
    """
    async with session_maker() as session:
        chats = await chat_crud.get_bound_with_schedule(session)
        for chat in chats:
            schedule = chat.schedule
            if schedule is None:
                continue
            now = datetime.now(ZoneInfo(schedule.timezone))
            if now.hour != DAILY_SCHEDULE_HOUR:
                continue
            lessons = sorted(
                schedule.lessons,
                key=lambda lesson: (lesson.weekday, lesson.start_time),
            )
            text = format_day(schedule, lessons, now.date(), show_empty=False)
            if text is None:
                continue
            try:
                await bot.send_message(
                    chat.id,
                    f'{DAILY_SCHEDULE_HEADER}\n\n{text}',
                )
            except TelegramForbiddenError:
                # Бота удалили из группы - отвязываем, чтобы не слать зря.
                logger.info('Бот удалён из группы %s, отвязываю', chat.id)
                await chat_crud.update(session, chat, {'schedule_id': None})
            except TelegramBadRequest:
                logger.exception(
                    'Не удалось отправить расписание в %s', chat.id
                )
        await session.commit()
