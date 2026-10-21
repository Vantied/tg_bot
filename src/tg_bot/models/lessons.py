import enum
import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    SmallInteger,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tg_bot.core.constants import (
    LESSON_ROOM_MAX_LENGTH,
    LESSON_SUBJECT_MAX_LENGTH,
    LESSON_TEACHER_MAX_LENGTH,
    MONDAY,
    SUNDAY,
)
from tg_bot.models.base import Base, IntIdMixin

if TYPE_CHECKING:
    from tg_bot.models.schedules import Schedule


class WeekType(enum.StrEnum):
    """По каким неделям идёт занятие."""

    EVERY = 'every'
    FIRST = 'first'
    SECOND = 'second'


class Lesson(IntIdMixin, Base):
    """Одно занятие в расписании."""

    __tablename__ = 'lessons'
    __table_args__ = (
        CheckConstraint(
            f'weekday BETWEEN {MONDAY} AND {SUNDAY}',
            name='weekday',
        ),
        CheckConstraint('end_time > start_time', name='time_order'),
        Index('ix_lessons_schedule_id_weekday', 'schedule_id', 'weekday'),
    )

    schedule_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('schedules.id', ondelete='CASCADE'),
    )
    weekday: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    subject: Mapped[str] = mapped_column(String(LESSON_SUBJECT_MAX_LENGTH))
    room: Mapped[str | None] = mapped_column(String(LESSON_ROOM_MAX_LENGTH))
    teacher: Mapped[str | None] = mapped_column(
        String(LESSON_TEACHER_MAX_LENGTH),
    )
    week_type: Mapped[WeekType] = mapped_column(
        Enum(
            WeekType,
            name='week_type',
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        server_default=WeekType.EVERY.value,
    )

    schedule: Mapped['Schedule'] = relationship(back_populates='lessons')
