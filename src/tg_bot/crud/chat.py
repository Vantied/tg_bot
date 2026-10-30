import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tg_bot.crud.base import CRUDBase
from tg_bot.models.chats import Chat
from tg_bot.models.schedules import Schedule


class CRUDChat(CRUDBase[Chat]):
    """CRUD операции для Chat."""

    async def get_by_schedule(
        self,
        session: AsyncSession,
        schedule_id: uuid.UUID,
    ) -> Sequence[Chat]:
        """Группы, привязанные к расписанию."""
        stmt = (
            select(self.model)
            .where(self.model.schedule_id == schedule_id)
            .order_by(self.model.title)
        )
        return (await session.scalars(stmt)).all()

    async def get_bound_with_schedule(
        self,
        session: AsyncSession,
    ) -> Sequence[Chat]:
        """Все привязанные группы сразу с расписанием и занятиями."""
        stmt = (
            select(self.model)
            .where(self.model.schedule_id.is_not(None))
            .options(
                selectinload(self.model.schedule).selectinload(
                    Schedule.lessons,
                ),
            )
        )
        return (await session.scalars(stmt)).all()


chat_crud = CRUDChat(Chat)
