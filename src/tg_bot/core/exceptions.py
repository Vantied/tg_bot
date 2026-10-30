class BadRequestToBD(Exception):
    """Ошибка при работе с БД."""


class ScheduleFileReadError(Exception):
    """Файл расписания не удалось прочитать как таблицу."""
