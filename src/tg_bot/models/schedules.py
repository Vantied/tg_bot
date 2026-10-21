from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    SmallInteger,
    String,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tg_bot.core.constants import (
    DEFAULT_TIMEZONE,
    FIRST_WEEK,
    SCHEDULE_TITLE_MAX_LENGTH,
    SECOND_WEEK,
    TIMEZONE_MAX_LENGTH,
)
from tg_bot.models.base import Base, CreatedAtMixin, UUIDIdMixin

if TYPE_CHECKING:
    from tg_bot.models.chats import Chat
    from tg_bot.models.lessons import Lesson
    from tg_bot.models.users import User


class Schedule(UUIDIdMixin, CreatedAtMixin, Base):
    """Расписание, которым управляет его владелец."""

    __tablename__ = 'schedules'
    __table_args__ = (
        CheckConstraint(
            f'anchor_week IN ({FIRST_WEEK}, {SECOND_WEEK})',
            name='anchor_week',
        ),
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(SCHEDULE_TITLE_MAX_LENGTH))
    is_two_weeks: Mapped[bool] = mapped_column(server_default=true())
    anchor_week: Mapped[int | None] = mapped_column(SmallInteger)
    anchor_monday: Mapped[date | None] = mapped_column(Date)
    timezone: Mapped[str] = mapped_column(
        String(TIMEZONE_MAX_LENGTH),
        server_default=DEFAULT_TIMEZONE,
    )

    owner: Mapped['User'] = relationship(back_populates='schedules')
    lessons: Mapped[list['Lesson']] = relationship(
        back_populates='schedule',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    chats: Mapped[list['Chat']] = relationship(
        back_populates='schedule',
        passive_deletes=True,
    )
