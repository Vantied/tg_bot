import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.models.base import Base


class CRUDBase[ModelT: Base]:
    """Базовый класс CRUD операций для моделей SQLAlchemy."""

    def __init__(
        self,
        model: type[ModelT],
    ) -> None:
        """Инициализирует CRUD класс."""
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        obj_id: int | uuid.UUID,
    ) -> ModelT | None:
        """Возвращает обьект модели по первичному ключу."""
        return await session.get(self.model, obj_id)

    async def create(
        self,
        session: AsyncSession,
        obj_in: dict[str, Any],
    ) -> ModelT:
        """Создает новый объект модели в БД."""
        db_obj = self.model(**obj_in)
        session.add(db_obj)
        await session.flush()
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelT,
        obj_in: dict[str, Any],
    ) -> ModelT:
        """Меняет поля объекта модели."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        await session.flush()
        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        db_obj: ModelT,
    ) -> None:
        """Удаляет объект модели из БД."""
        await session.delete(db_obj)
        await session.flush()
