import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tg_bot.core.constants import CHAT_TITLE_MAX_LENGTH
from tg_bot.models.base import Base, TelegramIdMixin, TimestampNow

if TYPE_CHECKING:
    from tg_bot.models.schedules import Schedule
    from tg_bot.models.users import User


class Chat(TelegramIdMixin, Base):
    """Группа Telegram, к которой привязано расписание."""

    __tablename__ = 'chats'

    schedule_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey('schedules.id', ondelete='SET NULL'),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(CHAT_TITLE_MAX_LENGTH))
    bound_by: Mapped[int | None] = mapped_column(
        ForeignKey('users.id', ondelete='SET NULL'),
    )
    bound_at: Mapped[TimestampNow]

    schedule: Mapped['Schedule | None'] = relationship(
        back_populates='chats',
    )
    binder: Mapped['User | None'] = relationship()
