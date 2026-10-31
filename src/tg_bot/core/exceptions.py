class BadRequestToBD(Exception):
    """Ошибка при работе с БД."""


class ScheduleFileReadError(Exception):
    """Файл расписания не удалось прочитать как таблицу."""


class BotValidationError(Exception):
    """Ошибка проверки данных: текст уходит пользователю.

    Поднимается в валидаторах, перехватывается ValidationErrorMiddleware,
    который отвечает пользователю и прерывает обработку команды.
    """

    def __init__(self, message: str) -> None:
        """Сохраняет текст ответа пользователю."""
        super().__init__(message)
        self.message = message
