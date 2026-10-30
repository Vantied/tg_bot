from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.models.schedules import Schedule
from tg_bot.crud.base import CRUDBase


class CRUDSchedule(CRUDBase[Schedule]):
    """КРУД операции для Schedule."""

    async def get_by_owner(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> Schedule | None:
        """Получить расписание по id пользователя."""
        stmt = select(self.model).where(self.model.owner_id == user_id)
        return await session.scalar(stmt)


schedule_crud = CRUDSchedule(Schedule)
