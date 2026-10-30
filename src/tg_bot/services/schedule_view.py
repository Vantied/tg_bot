import math
from collections.abc import Sequence
from datetime import date, datetime, time, timedelta

from aiogram import html

from tg_bot.core.constants import (
    DAY_HEADER,
    FIRST_WEEK,
    LESSON_LINE,
    LESSON_ROOM,
    LESSON_TEACHER,
    MINUTES_IN_HOUR,
    MONTH_NAMES,
    NEXT_LESSON_MESSAGE,
    NO_LESSON_NOW_MESSAGE,
    NO_LESSONS_DAY,
    NO_LESSONS_WEEK,
    NO_MORE_LESSONS_TODAY_MESSAGE,
    NOW_LESSON_MESSAGE,
    TIME_OUTPUT_FORMAT,
    WAIT_HOURS,
    WAIT_MINUTES,
    WAIT_WHOLE_HOURS,
    WEEK_NUMBER_SUFFIX,
    WEEKDAY_NAMES,
)
from tg_bot.models import Lesson, Schedule, WeekType
from tg_bot.services.weeks import DAYS_IN_WEEK, monday_of, week_number

SECONDS_IN_MINUTE = 60


def lessons_for_day(
    schedule: Schedule,
    lessons: Sequence[Lesson],
    day: date,
) -> list[Lesson]:
    """Занятия на дату с учётом чётной и нечётной недели."""
    week = week_number(schedule, day)
    allowed = {WeekType.EVERY}
    if week is not None:
        allowed.add(WeekType.FIRST if week == FIRST_WEEK else WeekType.SECOND)
    return [
        lesson
        for lesson in lessons
        if lesson.weekday == day.weekday() and lesson.week_type in allowed
    ]


def format_day(
    schedule: Schedule,
    lessons: Sequence[Lesson],
    day: date,
    *,
    show_empty: bool = True,
) -> str | None:
    """Расписание на один день. None - если занятий нет и show_empty=False."""
    day_lessons = lessons_for_day(schedule, lessons, day)
    if not day_lessons and not show_empty:
        return None
    header = DAY_HEADER.format(
        weekday=WEEKDAY_NAMES[day.weekday()],
        day=day.day,
        month=MONTH_NAMES[day.month - 1],
    )
    week = week_number(schedule, day)
    if week is not None:
        header += WEEK_NUMBER_SUFFIX.format(week=week)
    lines = [format_lesson(lesson) for lesson in day_lessons]
    return '\n'.join([header, *(lines or [NO_LESSONS_DAY])])


def format_week(
    schedule: Schedule,
    lessons: Sequence[Lesson],
    day: date,
) -> str:
    """Расписание на неделю, в которую попадает дата (только дни с парами)."""
    monday = monday_of(day)
    days = (monday + timedelta(days=offset) for offset in range(DAYS_IN_WEEK))
    blocks = [
        block
        for current in days
        if (block := format_day(schedule, lessons, current, show_empty=False))
    ]
    return '\n\n'.join(blocks) or NO_LESSONS_WEEK


def format_now(
    schedule: Schedule,
    lessons: Sequence[Lesson],
    now: datetime,
) -> str:
    """Какая пара идёт сейчас и какая следующая сегодня.

    now - время в часовом поясе расписания.
    """
    day_lessons = lessons_for_day(schedule, lessons, now.date())
    current_time = now.time().replace(tzinfo=None)
    current = next(
        (
            lesson
            for lesson in day_lessons
            if lesson.start_time <= current_time < lesson.end_time
        ),
        None,
    )
    upcoming = next(
        (lesson for lesson in day_lessons if lesson.start_time > current_time),
        None,
    )
    if current is not None:
        parts = [
            NOW_LESSON_MESSAGE.format(
                lesson=format_lesson(current),
                minutes=minutes_until(now, current.end_time),
            ),
        ]
    else:
        parts = [NO_LESSON_NOW_MESSAGE]
    if upcoming is not None:
        parts.append(
            NEXT_LESSON_MESSAGE.format(
                lesson=format_lesson(upcoming),
                wait=format_wait(minutes_until(now, upcoming.start_time)),
            ),
        )
    else:
        parts.append(NO_MORE_LESSONS_TODAY_MESSAGE)
    return '\n\n'.join(parts)


def minutes_until(now: datetime, moment: time) -> int:
    """Сколько минут от now до времени moment сегодня (с округлением вверх)."""
    target = datetime.combine(now.date(), moment, tzinfo=now.tzinfo)
    return math.ceil((target - now).total_seconds() / SECONDS_IN_MINUTE)


def format_wait(minutes: int) -> str:
    """45 -> «45 мин.», 135 -> «2 ч 15 мин.»."""
    if minutes < MINUTES_IN_HOUR:
        return WAIT_MINUTES.format(minutes=minutes)
    hours, rest = divmod(minutes, MINUTES_IN_HOUR)
    if rest == 0:
        return WAIT_WHOLE_HOURS.format(hours=hours)
    return WAIT_HOURS.format(hours=hours, minutes=rest)


def format_lesson(lesson: Lesson) -> str:
    """Одна строка: время, предмет, кабинет, преподаватель."""
    line = LESSON_LINE.format(
        start=lesson.start_time.strftime(TIME_OUTPUT_FORMAT),
        end=lesson.end_time.strftime(TIME_OUTPUT_FORMAT),
        subject=html.quote(lesson.subject),
    )
    if lesson.room:
        line += LESSON_ROOM.format(room=html.quote(lesson.room))
    if lesson.teacher:
        line += LESSON_TEACHER.format(teacher=html.quote(lesson.teacher))
    return line
