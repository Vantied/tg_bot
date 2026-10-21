import uuid
from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from tg_bot.core.constants import PRIMARY_KEY_SORT_ORDER

NAMING_CONVENTION = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}

TimestampNow = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]


class Base(DeclarativeBase):
    """Базовый класс декларативных моделей."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class IntIdMixin:
    """Целочисленный первичный ключ с автоинкрементом."""

    id: Mapped[int] = mapped_column(
        primary_key=True,
        sort_order=PRIMARY_KEY_SORT_ORDER,
    )


class UUIDIdMixin:
    """Первичный ключ UUID, генерируется на стороне приложения."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
        sort_order=PRIMARY_KEY_SORT_ORDER,
    )


class TelegramIdMixin:
    """Первичный ключ из id Telegram, поэтому без автоинкремента."""

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
        sort_order=PRIMARY_KEY_SORT_ORDER,
    )


class CreatedAtMixin:
    """Добавляет колонку с датой создания записи."""

    created_at: Mapped[TimestampNow]
