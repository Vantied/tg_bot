from aiogram.fsm.state import State, StatesGroup


class NewSchedule(StatesGroup):
    """Класс для состояния."""

    title = State()
    city = State()
    two_weeks = State()
    current_week = State()
    waiting_file = State()


class BindChat(StatesGroup):
    """Состояние для /bind: ждём id группы."""

    chat_id = State()
