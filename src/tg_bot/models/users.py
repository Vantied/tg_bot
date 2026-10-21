from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tg_bot.core.constants import USER_FULL_NAME_MAX_LENGTH
from tg_bot.models.base import Base, CreatedAtMixin, TelegramIdMixin

if TYPE_CHECKING:
    from tg_bot.models.schedules import Schedule


class User(TelegramIdMixin, CreatedAtMixin, Base):
    """Пользователь Telegram."""

    __tablename__ = 'users'

    full_name: Mapped[str] = mapped_column(String(USER_FULL_NAME_MAX_LENGTH))

    schedules: Mapped[list['Schedule']] = relationship(
        back_populates='owner',
    )
