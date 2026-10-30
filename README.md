# tg_bot

Telegram-бот с расписанием занятий (в том числе чётная/нечётная неделя),
погодой и котиками. Стек: Python 3.12, aiogram 3, SQLAlchemy 2.0 (async),
PostgreSQL, Alembic.

## Настройки

Скопируй `.env.example` в `.env` и заполни:

| Переменная | Что это |
|---|---|
| `TOKEN` | токен бота от @BotFather |
| `postgres_user` | пользователь базы |
| `postgres_password` | пароль базы |
| `postgres_db` | имя базы |
| `postgres_server` | адрес базы (`localhost` для локального запуска) |
| `postgres_port` | порт базы (`5432`) |

## Запуск в Docker

```bash
docker compose up -d --build
```

Поднимаются два контейнера:

- `db` — PostgreSQL 17. Пользователь и база создаются при первом запуске
  из `postgres_user`, `postgres_password`, `postgres_db`. Данные хранятся
  в томе `pgdata`, поэтому не пропадают при перезапуске.
- `bot` — бот. Ждёт, пока база будет готова, применяет миграции
  (`alembic upgrade head`) и запускается.

`postgres_server` и `postgres_port` из `.env` в Docker не используются:
внутри Docker бот ходит в базу по имени сервиса `db`.

Полезные команды:

```bash
docker compose logs -f bot
```

```bash
docker compose restart bot
```

```bash
docker compose down
```

`docker compose down -v` удалит и том с базой — все данные пропадут.

## Локальный запуск (без Docker)

Нужен запущенный PostgreSQL и uv.

```bash
uv sync
```

```bash
uv run alembic upgrade head
```

```bash
uv run tg-bot
```

Нельзя одновременно запускать бота локально и в Docker с одним токеном:
Telegram отдаёт обновления только одной копии (`TelegramConflictError`).
