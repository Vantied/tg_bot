import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.crud.base import CRUDBase
from tg_bot.models.lessons import Lesson


class CRUDLesson(CRUDBase[Lesson]):
    """CRUD операции для Lesson."""

    async def get_by_schedule(
        self,
        session: AsyncSession,
        schedule_id: uuid.UUID,
    ) -> Sequence[Lesson]:
        """Возвращает занятия расписания по дням и времени."""
        stmt = (
            select(self.model)
            .where(self.model.schedule_id == schedule_id)
            .order_by(self.model.weekday, self.model.start_time)
        )
        return (await session.scalars(stmt)).all()

    async def replace_for_schedule(
        self,
        session: AsyncSession,
        schedule_id: uuid.UUID,
        lessons: Sequence[dict[str, Any]],
    ) -> int:
        """Заменяет все занятия расписания новыми.

        Старые и новые занятия меняются в одной транзакции:
        при ошибке middleware откатит всё целиком.
        """
        await session.execute(
            delete(self.model).where(self.model.schedule_id == schedule_id),
        )
        session.add_all(
            self.model(schedule_id=schedule_id, **lesson) for lesson in lessons
        )
        await session.flush()
        return len(lessons)


lesson_crud = CRUDLesson(Lesson)
