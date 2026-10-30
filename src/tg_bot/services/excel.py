from collections.abc import Sequence
from datetime import datetime, time
from io import BytesIO
from typing import Any, BinaryIO

import pandas as pd
from openpyxl.utils import get_column_letter

from tg_bot.core.constants import (
    BAD_DAY_ERROR,
    BAD_TIME_ERROR,
    BAD_WEEK_ERROR,
    COLUMN_DAY,
    COLUMN_END,
    COLUMN_ROOM,
    COLUMN_START,
    COLUMN_SUBJECT,
    COLUMN_TEACHER,
    COLUMN_WEEK,
    EMPTY_SUBJECT_ERROR,
    LESSON_ROOM_MAX_LENGTH,
    LESSON_SUBJECT_MAX_LENGTH,
    LESSON_TEACHER_MAX_LENGTH,
    MAX_LESSONS_IN_FILE,
    MISSING_COLUMNS_ERROR,
    REQUIRED_COLUMNS,
    ROW_ERROR,
    TEMPLATE_COLUMNS,
    TEMPLATE_EXAMPLE_ROWS,
    TIME_FORMATS,
    TIME_ORDER_ERROR,
    TIME_OUTPUT_FORMAT,
    TOO_LONG_ERROR,
    TOO_MANY_LESSONS_ERROR,
    WEEK_EVERY_VALUE,
    WEEK_FIRST_VALUE,
    WEEK_SECOND_VALUE,
    WEEKDAY_FULL_NAMES,
    WEEKDAY_SHORT_NAMES,
)
from tg_bot.core.exceptions import ScheduleFileReadError
from tg_bot.models import Lesson, WeekType

# Первая строка листа - заголовки, данные начинаются со второй.
FIRST_DATA_ROW = 2
SHEET_NAME = 'Расписание'
COLUMN_WIDTH = 18

WEEKDAY_BY_NAME = {
    name.lower(): index
    for names in (WEEKDAY_SHORT_NAMES, WEEKDAY_FULL_NAMES)
    for index, name in enumerate(names)
}
WEEK_TYPE_BY_VALUE = {
    '': WeekType.EVERY,
    WEEK_EVERY_VALUE: WeekType.EVERY,
    WEEK_FIRST_VALUE: WeekType.FIRST,
    WEEK_SECOND_VALUE: WeekType.SECOND,
}
WEEK_VALUE_BY_TYPE = {
    WeekType.EVERY: WEEK_EVERY_VALUE,
    WeekType.FIRST: WEEK_FIRST_VALUE,
    WeekType.SECOND: WEEK_SECOND_VALUE,
}
OPTIONAL_LIMITS = (
    (COLUMN_ROOM, 'room', LESSON_ROOM_MAX_LENGTH),
    (COLUMN_TEACHER, 'teacher', LESSON_TEACHER_MAX_LENGTH),
)


def build_template(lessons: Sequence[Lesson]) -> bytes:
    """Собирает .xlsx с занятиями, а если их нет - с примерами."""
    rows = [lesson_to_row(lesson) for lesson in lessons]
    frame = pd.DataFrame(
        rows or TEMPLATE_EXAMPLE_ROWS,
        columns=list(TEMPLATE_COLUMNS),
    )
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        frame.to_excel(writer, index=False, sheet_name=SHEET_NAME)
        sheet = writer.sheets[SHEET_NAME]
        for index in range(1, len(TEMPLATE_COLUMNS) + 1):
            sheet.column_dimensions[
                get_column_letter(index)
            ].width = COLUMN_WIDTH
    return buffer.getvalue()


def lesson_to_row(lesson: Lesson) -> tuple[str, ...]:
    """Превращает занятие в строку таблицы."""
    return (
        WEEKDAY_SHORT_NAMES[lesson.weekday],
        lesson.start_time.strftime(TIME_OUTPUT_FORMAT),
        lesson.end_time.strftime(TIME_OUTPUT_FORMAT),
        lesson.subject,
        lesson.room or '',
        lesson.teacher or '',
        WEEK_VALUE_BY_TYPE[lesson.week_type],
    )


def parse_schedule(
    file: BinaryIO,
    *,
    is_two_weeks: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Разбирает таблицу и возвращает занятия и список ошибок.

    Если ошибок нет, занятия готовы к сохранению.
    """
    try:
        frame = pd.read_excel(file, dtype=str, engine='openpyxl')
    except Exception as error:
        raise ScheduleFileReadError from error

    frame.columns = [str(column).strip() for column in frame.columns]
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        return [], [MISSING_COLUMNS_ERROR.format(columns=', '.join(missing))]
    for column in TEMPLATE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ''
    frame = frame.fillna('')

    lessons: list[dict[str, Any]] = []
    errors: list[str] = []
    records = frame.to_dict('records')
    for row_number, record in enumerate(records, start=FIRST_DATA_ROW):
        values = {
            column: str(record[column]).strip() for column in TEMPLATE_COLUMNS
        }
        if not any(values.values()):
            continue
        lesson, row_errors = parse_row(values, is_two_weeks=is_two_weeks)
        errors.extend(
            ROW_ERROR.format(row=row_number, error=error)
            for error in row_errors
        )
        if lesson is not None:
            lessons.append(lesson)

    if len(lessons) > MAX_LESSONS_IN_FILE:
        errors.append(TOO_MANY_LESSONS_ERROR)
    return lessons, errors


def parse_row(
    values: dict[str, str],
    *,
    is_two_weeks: bool,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Проверяет одну строку таблицы."""
    errors: list[str] = []
    weekday = check_weekday(values, errors)
    start_time, end_time = check_times(values, errors)
    check_lengths(values, errors)
    week_type = check_week(values, errors) if is_two_weeks else WeekType.EVERY
    if errors:
        return None, errors
    lesson = {
        'weekday': weekday,
        'start_time': start_time,
        'end_time': end_time,
        'subject': values[COLUMN_SUBJECT],
        'week_type': week_type,
    }
    for column, field, _ in OPTIONAL_LIMITS:
        lesson[field] = values[column] or None
    return lesson, []


def check_weekday(values: dict[str, str], errors: list[str]) -> int | None:
    """День недели: Пн-Вс или полное название."""
    weekday = WEEKDAY_BY_NAME.get(values[COLUMN_DAY].lower())
    if weekday is None:
        errors.append(BAD_DAY_ERROR.format(value=values[COLUMN_DAY]))
    return weekday


def check_times(
    values: dict[str, str],
    errors: list[str],
) -> tuple[time | None, time | None]:
    """Время начала и конца, конец позже начала."""
    parsed = []
    for column in (COLUMN_START, COLUMN_END):
        value = parse_time(values[column])
        if value is None:
            errors.append(
                BAD_TIME_ERROR.format(column=column, value=values[column]),
            )
        parsed.append(value)
    start_time, end_time = parsed
    if start_time and end_time and end_time <= start_time:
        errors.append(TIME_ORDER_ERROR)
    return start_time, end_time


def check_lengths(values: dict[str, str], errors: list[str]) -> None:
    """Предмет обязателен, у текстовых полей есть лимит длины."""
    if not values[COLUMN_SUBJECT]:
        errors.append(EMPTY_SUBJECT_ERROR)
    limits = (
        (COLUMN_SUBJECT, LESSON_SUBJECT_MAX_LENGTH),
        *((column, limit) for column, _, limit in OPTIONAL_LIMITS),
    )
    for column, limit in limits:
        if len(values[column]) > limit:
            errors.append(TOO_LONG_ERROR.format(column=column, limit=limit))


def check_week(values: dict[str, str], errors: list[str]) -> WeekType:
    """Неделя: каждая, 1 или 2. Пустая ячейка - каждая."""
    week_value = values[COLUMN_WEEK].lower().removesuffix('.0')
    week_type = WEEK_TYPE_BY_VALUE.get(week_value)
    if week_type is None:
        errors.append(BAD_WEEK_ERROR.format(value=values[COLUMN_WEEK]))
        return WeekType.EVERY
    return week_type


def parse_time(value: str) -> time | None:
    """Разбирает время ЧЧ:ММ (Excel может прислать и ЧЧ:ММ:СС)."""
    for time_format in TIME_FORMATS:
        try:
            return datetime.strptime(value, time_format).time()
        except ValueError:
            continue
    return None
