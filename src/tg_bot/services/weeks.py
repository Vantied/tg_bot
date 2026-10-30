from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def current_monday(timezone: str) -> date:
    """Возвращает понедельник текущей недели в указанном часовом поясе."""
    today = datetime.now(ZoneInfo(timezone)).date()
    return today - timedelta(days=today.weekday())
