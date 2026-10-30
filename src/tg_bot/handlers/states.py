from aiogram.fsm.state import State, StatesGroup


class NewSchedule(StatesGroup):
    """Класс для состояния."""

    title = State()
    two_weeks = State()
    current_week = State()
    waiting_file = State()
