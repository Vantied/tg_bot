from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.crud.user import user_crud
from tg_bot.crud.schedule import schedule_crud


async def validate_user_exist(session: AsyncSession, user_id: int) -> bool:
    """Проверяет существует ли пользователь."""
    user = await user_crud.get(session, user_id)
    return user is not None


async def validate_schedule_exist(session: AsyncSession, user_id: int) -> bool:
    """Проверяет существует ли у пользователя расписание."""
    schedule = await schedule_crud.get_by_owner(session, user_id)
    return schedule is not None
