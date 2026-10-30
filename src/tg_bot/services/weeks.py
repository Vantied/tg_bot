from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from tg_bot.core.constants import FIRST_WEEK, SECOND_WEEK, TIME_OUTPUT_FORMAT
from tg_bot.models import Schedule

DAYS_IN_WEEK = 7


def current_monday(timezone: str) -> date:
    """Возвращает понедельник текущей недели в указанном часовом поясе."""
    return monday_of(local_today(timezone))


def local_now(timezone: str) -> datetime:
    """Текущие дата и время в указанном часовом поясе."""
    return datetime.now(ZoneInfo(timezone))


def local_today(timezone: str) -> date:
    """Сегодняшняя дата в указанном часовом поясе."""
    return local_now(timezone).date()


def local_time_text(timezone: str) -> str:
    """Текущее время в поясе в виде ЧЧ:ММ."""
    return local_now(timezone).strftime(TIME_OUTPUT_FORMAT)


def monday_of(day: date) -> date:
    """Понедельник недели, в которую попадает дата."""
    return day - timedelta(days=day.weekday())


def other_week(week: int) -> int:
    """1 -> 2, 2 -> 1."""
    return SECOND_WEEK if week == FIRST_WEEK else FIRST_WEEK


def week_number(schedule: Schedule, day: date) -> int | None:
    """Номер недели (1 или 2) для даты. None - расписание на 7 дней.

    Считаем, сколько недель прошло от anchor_monday: чётное число -
    та же неделя, что указал пользователь, нечётное - другая.
    """
    if (
        not schedule.is_two_weeks
        or schedule.anchor_week is None
        or schedule.anchor_monday is None
    ):
        return None
    weeks_passed = (monday_of(day) - schedule.anchor_monday).days
    weeks_passed //= DAYS_IN_WEEK
    if weeks_passed % 2 == 0:
        return schedule.anchor_week
    return other_week(schedule.anchor_week)
