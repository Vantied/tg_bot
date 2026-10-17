from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие настройки
    token: str

    # Настройки подключения к БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_server: str
    postgres_port: int

    @property
    def db_url(self) -> str:
        """Строка подключения к БД."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
